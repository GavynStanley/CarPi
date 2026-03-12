#!/bin/bash -e
# =============================================================================
# 02-signalkit-app/00-run.sh — SignalKit Qt/QML Edition
# =============================================================================
# Installs the SignalKit Python application into the image at /opt/signalkit.
# Uses PySide6 + QML for rendering directly to the framebuffer via EGLFS.
# No X11, no WebKit, no browser engine.
# =============================================================================

echo "==> [02-signalkit-app] Installing SignalKit application"

SIGNALKIT_DEST="${ROOTFS_DIR}/opt/signalkit"
SIGNALKIT_REPO="https://github.com/GavynStanley/SignalKit.git"

# ---------------------------------------------------------------------------
# 1. Clone the SignalKit repo into the image (enables OTA updates via git pull)
# ---------------------------------------------------------------------------
install -d "${SIGNALKIT_DEST}"

if git clone --depth=1 "${SIGNALKIT_REPO}" "${SIGNALKIT_DEST}.tmp" 2>/dev/null; then
    rm -rf "${SIGNALKIT_DEST}"
    mv "${SIGNALKIT_DEST}.tmp" "${SIGNALKIT_DEST}"
    echo "Cloned SignalKit repo from ${SIGNALKIT_REPO}"
else
    echo "Git clone failed (offline?) — falling back to file copy"
    REPO_ROOT="$(dirname "$(dirname "${STAGE_DIR}")")"
    APP_SRC="${REPO_ROOT}/signalkit"

    if [[ -d "${APP_SRC}" ]]; then
        install -d "${SIGNALKIT_DEST}/signalkit"
        cp -r "${APP_SRC}/." "${SIGNALKIT_DEST}/signalkit/"
        [[ -f "${REPO_ROOT}/VERSION" ]] && cp "${REPO_ROOT}/VERSION" "${SIGNALKIT_DEST}/"
        echo "Copied SignalKit source from ${APP_SRC} -> ${SIGNALKIT_DEST}/signalkit/"
    else
        echo "ERROR: SignalKit source not found at ${APP_SRC} and git clone failed."
        echo "Cannot build image without application source."
        exit 1
    fi
    echo "WARNING: OTA updates will not work without a git repo"
fi

on_chroot << 'EOF'
chown -R pi:pi /opt/signalkit
chmod +x /opt/signalkit/signalkit/main.py 2>/dev/null || true
EOF

echo "SignalKit installed to /opt/signalkit"

# ---------------------------------------------------------------------------
# 2. Install Python dependencies
# ---------------------------------------------------------------------------
# PyQt6 is installed via apt (see 00-packages). Only pip-install what apt lacks.
on_chroot << 'EOF'
echo "Installing Python packages: obd flask"
python3 -m pip install --break-system-packages obd flask 2>/dev/null \
    || python3 -m pip install obd flask

echo "Python packages installed:"
python3 -m pip show obd flask | grep -E "^(Name|Version):"
echo "PyQt6 (system):"
python3 -c "import PyQt6.QtCore; print('  PyQt6', PyQt6.QtCore.PYQT_VERSION_STR)"
EOF

# ---------------------------------------------------------------------------
# 3. Build and install UxPlay v1.71+ from source (AirPlay 2 casting support)
# ---------------------------------------------------------------------------
# The Debian repo version is too old for media casting (YouTube etc.).
# v1.71+ adds AirPlay HLS video streaming support.
on_chroot << 'EOF'
echo "Building UxPlay from source..."
UXPLAY_VERSION="v1.71"

cd /tmp
git clone --depth=1 --branch "${UXPLAY_VERSION}" \
    https://github.com/FDH2/UxPlay.git uxplay-src 2>/dev/null \
    || git clone --depth=1 https://github.com/FDH2/UxPlay.git uxplay-src

cd uxplay-src
mkdir build && cd build
cmake ..
make -j$(nproc)
make install
ldconfig

echo "UxPlay installed:"
uxplay -v 2>&1 || true

# Clean up build artifacts
cd /
rm -rf /tmp/uxplay-src

echo "UxPlay build complete"
EOF

# ---------------------------------------------------------------------------
# 4. Create a log directory that survives the read-only root
# ---------------------------------------------------------------------------
install -d -m 755 "${ROOTFS_DIR}/var/log/signalkit"
on_chroot << 'EOF'
chown pi:pi /var/log/signalkit
EOF

echo "==> [02-signalkit-app] Application install complete"
