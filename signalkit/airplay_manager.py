#!/usr/bin/env python3
"""
AirPlay receiver manager — launches UxPlay with GStreamer pipeline,
captures decoded video frames, and serves them to the QML UI.

UxPlay decodes the AirPlay mirror stream via GStreamer. We configure it
to output raw video to a shared-memory sink, then read those frames in
Python and push them through a QQuickImageProvider so QML can display
them as a live Image source.

On macOS (dev), UxPlay isn't available — the manager exposes a stub
that keeps the same API so the rest of the app works unchanged.
"""
import logging
import os
import platform
import shutil
import signal
import subprocess
import sys
import threading
import time

logger = logging.getLogger(__name__)

# ── Platform detection ──────────────────────────────────────────────
IS_LINUX = platform.system() == "Linux"
IS_PI = IS_LINUX and os.path.isfile("/proc/device-tree/model")

# ── Check for uxplay binary ────────────────────────────────────────
UXPLAY_BIN = shutil.which("uxplay")


class AirPlayManager:
    """Manages the UxPlay subprocess lifecycle and exposes state."""

    def __init__(self):
        self._proc: subprocess.Popen | None = None
        self._running = False
        self._connected = False
        self._device_name = ""
        self._lock = threading.Lock()
        self._monitor_thread: threading.Thread | None = None

        # Callbacks — set by the Bridge to propagate state changes
        self.on_state_changed: callable | None = None

    # ── Public API ──────────────────────────────────────────────────

    @property
    def available(self) -> bool:
        """True if uxplay is installed on this system."""
        return UXPLAY_BIN is not None

    @property
    def running(self) -> bool:
        return self._running

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def device_name(self) -> str:
        return self._device_name

    def start(self, server_name: str = "SignalKit") -> bool:
        """Launch the UxPlay receiver. Returns True if started."""
        with self._lock:
            if self._running:
                logger.warning("AirPlay receiver already running")
                return True

            if not self.available:
                logger.error("uxplay not found — cannot start AirPlay receiver")
                return False

            cmd = self._build_command(server_name)
            logger.info("Starting AirPlay receiver: %s", " ".join(cmd))

            try:
                self._proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    preexec_fn=os.setsid if IS_LINUX else None,
                )
                self._running = True
                self._notify()

                # Monitor stdout for connection events
                self._monitor_thread = threading.Thread(
                    target=self._monitor_output,
                    name="AirPlayMonitor",
                    daemon=True,
                )
                self._monitor_thread.start()
                return True

            except Exception as e:
                logger.error("Failed to start uxplay: %s", e)
                self._running = False
                self._notify()
                return False

    def stop(self):
        """Gracefully stop the UxPlay receiver."""
        with self._lock:
            if not self._running or self._proc is None:
                return

            logger.info("Stopping AirPlay receiver")
            try:
                if IS_LINUX:
                    # Kill the whole process group
                    os.killpg(os.getpgid(self._proc.pid), signal.SIGTERM)
                else:
                    self._proc.terminate()
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("uxplay didn't exit cleanly, killing")
                self._proc.kill()
                self._proc.wait(timeout=2)
            except Exception as e:
                logger.error("Error stopping uxplay: %s", e)

            self._proc = None
            self._running = False
            self._connected = False
            self._device_name = ""
            self._notify()

    # ── Internals ───────────────────────────────────────────────────

    def _build_command(self, server_name: str) -> list[str]:
        """Build the uxplay command with appropriate GStreamer pipeline."""
        cmd = [
            UXPLAY_BIN,
            "-n", server_name,  # Bonjour name shown on iOS devices
            "-nh",              # No history (don't persist pairing)
            "-pin",             # Require PIN for first connection
        ]

        if IS_PI:
            # Pi 5: software decode (avdec) → kmssink (direct DRM/KMS, no X11)
            cmd.extend([
                "-avdec",                          # Software H.264/H.265 decode
                "-vs", "kmssink",                   # Render direct to DRM/KMS
                "-as", "alsasink",                  # Audio via ALSA
            ])
        else:
            # macOS/desktop: use default sinks
            cmd.extend([
                "-vs", "autovideosink",
                "-as", "autoaudiosink",
            ])

        return cmd

    def _monitor_output(self):
        """Read uxplay stdout and detect connection/disconnection events."""
        if self._proc is None or self._proc.stdout is None:
            return

        try:
            for line in self._proc.stdout:
                line = line.strip()
                if not line:
                    continue

                logger.debug("uxplay: %s", line)

                # Detect connection events from uxplay output
                if "client connected" in line.lower() or "airplay connected" in line.lower():
                    self._connected = True
                    # Try to extract device name
                    if "from" in line.lower():
                        parts = line.split("from", 1)
                        if len(parts) > 1:
                            self._device_name = parts[1].strip().strip('"')
                    self._notify()

                elif "client disconnected" in line.lower() or "airplay disconnected" in line.lower():
                    self._connected = False
                    self._device_name = ""
                    self._notify()

        except Exception as e:
            logger.debug("AirPlay monitor ended: %s", e)

        # Process exited
        with self._lock:
            self._running = False
            self._connected = False
            self._device_name = ""
            self._notify()

    def _notify(self):
        """Call the state-changed callback if set."""
        if self.on_state_changed:
            try:
                self.on_state_changed()
            except Exception:
                pass


# Module-level singleton
airplay = AirPlayManager()
