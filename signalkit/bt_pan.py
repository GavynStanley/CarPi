#!/usr/bin/env python3
# =============================================================================
# bt_pan.py - Bluetooth PAN (Personal Area Network) Manager
# =============================================================================
# Connects to a paired phone via Bluetooth Network Access Point (NAP) profile
# so the Pi can piggyback on the phone's cellular data for internet access.
#
# Flow:
#   1. Phone pairs with Pi (initiated via web UI)
#   2. Phone enables Bluetooth tethering (Android/iOS setting)
#   3. This module connects to the phone's NAP profile
#   4. A bnep0 interface appears, DHCP gets an IP
#   5. Pi now has internet through the phone's cellular data
#
# Usage:
#   Called from main.py as a background thread, or standalone:
#     python3 bt_pan.py
# =============================================================================

import logging
import subprocess
import threading
import time

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Bluetooth PAN operations (all use subprocess for simplicity)
# ---------------------------------------------------------------------------

def bt_pair(mac: str) -> tuple[bool, str]:
    """Pair and trust a Bluetooth device. Returns (success, message)."""
    mac = mac.strip().upper()
    try:
        # Make Pi discoverable so phone can see it
        subprocess.run(["bluetoothctl", "discoverable", "on"],
                       capture_output=True, text=True, timeout=5)

        # Trust first (so auto-reconnect works)
        r = subprocess.run(["bluetoothctl", "trust", mac],
                           capture_output=True, text=True, timeout=10)
        if r.returncode != 0:
            return False, f"Trust failed: {r.stderr.strip()}"

        # Initiate pairing
        r = subprocess.run(["bluetoothctl", "pair", mac],
                           capture_output=True, text=True, timeout=30)
        output = r.stdout + r.stderr
        if "already exists" in output.lower() or r.returncode == 0:
            # Turn off discoverable after pairing
            subprocess.run(["bluetoothctl", "discoverable", "off"],
                           capture_output=True, text=True, timeout=5)
            return True, "Paired successfully"
        return False, f"Pair failed: {output.strip()}"
    except subprocess.TimeoutExpired:
        return False, "Pairing timed out — make sure your phone is ready to pair"
    except Exception as e:
        return False, str(e)


def bt_unpair(mac: str) -> tuple[bool, str]:
    """Remove a paired Bluetooth device."""
    mac = mac.strip().upper()
    try:
        r = subprocess.run(["bluetoothctl", "remove", mac],
                           capture_output=True, text=True, timeout=10)
        if r.returncode == 0 or "not available" in (r.stdout + r.stderr).lower():
            return True, "Device removed"
        return False, f"Remove failed: {r.stderr.strip()}"
    except Exception as e:
        return False, str(e)


def bt_connect_pan(mac: str) -> tuple[bool, str]:
    """Connect to a phone's Bluetooth PAN (NAP) profile.

    Returns (success, message). On success, a bnep0 interface is created.
    """
    mac = mac.strip().upper()
    obj_path = "/org/bluez/hci0/dev_" + mac.replace(":", "_")

    try:
        # First ensure the device is connected at the ACL level
        r = subprocess.run(["bluetoothctl", "connect", mac],
                           capture_output=True, text=True, timeout=15)
        output = r.stdout + r.stderr
        if r.returncode != 0 and "already connected" not in output.lower():
            return False, f"BT connect failed: {output.strip()}"

        # Small delay for profiles to register
        time.sleep(1)

        # Connect the Network1 (PAN) profile via D-Bus
        r = subprocess.run([
            "dbus-send", "--system", "--type=method_call",
            "--print-reply", "--dest=org.bluez",
            obj_path,
            "org.bluez.Network1.Connect",
            "string:nap"
        ], capture_output=True, text=True, timeout=15)

        if r.returncode != 0:
            err = r.stderr.strip()
            if "Already connected" in err:
                return True, "Already connected to PAN"
            return False, f"PAN connect failed: {err}"

        # The reply contains the interface name (usually "bnep0")
        interface = "bnep0"
        for line in r.stdout.splitlines():
            if "string" in line and "bnep" in line:
                interface = line.split('"')[1] if '"' in line else "bnep0"

        logger.info(f"BT PAN connected on {interface}")

        # Request an IP via DHCP on the new interface
        _run_dhcp(interface)

        return True, f"Connected via {interface}"

    except subprocess.TimeoutExpired:
        return False, "Connection timed out — is Bluetooth tethering enabled on your phone?"
    except Exception as e:
        return False, str(e)


def bt_disconnect_pan(mac: str) -> tuple[bool, str]:
    """Disconnect from a phone's Bluetooth PAN."""
    mac = mac.strip().upper()
    obj_path = "/org/bluez/hci0/dev_" + mac.replace(":", "_")

    try:
        subprocess.run([
            "dbus-send", "--system", "--type=method_call",
            "--print-reply", "--dest=org.bluez",
            obj_path,
            "org.bluez.Network1.Disconnect",
        ], capture_output=True, text=True, timeout=10)
        return True, "Disconnected"
    except Exception as e:
        return False, str(e)


def _run_dhcp(interface: str):
    """Request an IP address on the PAN interface."""
    # Kill any existing dhclient on this interface
    subprocess.run(["sudo", "dhclient", "-r", interface],
                   capture_output=True, timeout=5)
    # Request a new lease
    r = subprocess.run(["sudo", "dhclient", "-v", interface],
                       capture_output=True, text=True, timeout=20)
    if r.returncode == 0:
        logger.info(f"DHCP lease obtained on {interface}")
    else:
        # Fallback: try dhcpcd
        r2 = subprocess.run(["sudo", "dhcpcd", interface],
                            capture_output=True, text=True, timeout=20)
        if r2.returncode == 0:
            logger.info(f"DHCP lease obtained on {interface} (dhcpcd)")
        else:
            logger.warning(f"DHCP failed on {interface}: {r.stderr.strip()} / {r2.stderr.strip()}")


def is_pan_connected(mac: str) -> bool:
    """Check if the PAN connection to the given MAC is active."""
    mac = mac.strip().upper()
    obj_path = "/org/bluez/hci0/dev_" + mac.replace(":", "_")
    try:
        r = subprocess.run([
            "dbus-send", "--system", "--print-reply", "--dest=org.bluez",
            obj_path,
            "org.freedesktop.DBus.Properties.Get",
            "string:org.bluez.Network1", "string:Connected"
        ], capture_output=True, text=True, timeout=5)
        return "boolean true" in r.stdout
    except Exception:
        return False


def is_phone_nearby(mac: str) -> bool:
    """Check if a paired phone is within Bluetooth range."""
    mac = mac.strip().upper()
    try:
        r = subprocess.run(["bluetoothctl", "info", mac],
                           capture_output=True, text=True, timeout=5)
        return "Connected: yes" in r.stdout
    except Exception:
        return False


def get_pan_status() -> dict:
    """Get current PAN connection status."""
    status = {
        "connected": False,
        "interface": None,
        "ip": None,
        "has_internet": False,
    }
    try:
        # Check if bnep0 exists and has an IP
        r = subprocess.run(["ip", "addr", "show", "bnep0"],
                           capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            status["interface"] = "bnep0"
            status["connected"] = True
            for line in r.stdout.splitlines():
                line = line.strip()
                if line.startswith("inet "):
                    status["ip"] = line.split()[1].split("/")[0]
                    break

            # Quick connectivity check
            r2 = subprocess.run(
                ["ping", "-c", "1", "-W", "2", "8.8.8.8"],
                capture_output=True, timeout=5,
            )
            status["has_internet"] = r2.returncode == 0
    except Exception:
        pass
    return status


# ---------------------------------------------------------------------------
# Background auto-connect loop
# ---------------------------------------------------------------------------

class BtPanManager(threading.Thread):
    """Background thread that maintains Bluetooth PAN connection to phone.

    Periodically checks if the phone is paired and nearby, then connects
    to its PAN profile for internet access. Reconnects automatically if
    the connection drops.
    """

    def __init__(self, phone_mac: str, check_interval: int = 30):
        super().__init__(name="BtPanManager", daemon=True)
        self.phone_mac = phone_mac.strip().upper()
        self.check_interval = check_interval
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        if not self.phone_mac or self.phone_mac == "":
            logger.info("BT PAN: No phone MAC configured, manager idle")
            return

        logger.info(f"BT PAN manager started for {self.phone_mac}")

        while not self._stop_event.is_set():
            try:
                if not is_pan_connected(self.phone_mac):
                    logger.info(f"BT PAN: Attempting connection to {self.phone_mac}")
                    ok, msg = bt_connect_pan(self.phone_mac)
                    if ok:
                        logger.info(f"BT PAN: {msg}")
                    else:
                        logger.debug(f"BT PAN: {msg}")
            except Exception as e:
                logger.debug(f"BT PAN manager error: {e}")

            self._stop_event.wait(self.check_interval)

        # Cleanup on stop
        try:
            bt_disconnect_pan(self.phone_mac)
        except Exception:
            pass
        logger.info("BT PAN manager stopped")


# ---------------------------------------------------------------------------
# Standalone entry point (for testing)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(message)s")

    if len(sys.argv) < 2:
        print("Usage: python3 bt_pan.py <PHONE_MAC>")
        print("       python3 bt_pan.py AA:BB:CC:DD:EE:FF")
        sys.exit(1)

    mac = sys.argv[1]
    print(f"Connecting to {mac}...")
    ok, msg = bt_connect_pan(mac)
    print(f"Result: {msg}")
    if ok:
        status = get_pan_status()
        print(f"Status: {status}")
