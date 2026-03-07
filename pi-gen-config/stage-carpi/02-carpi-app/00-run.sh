#!/bin/bash -e
# =============================================================================
# 02-carpi-app/00-run.sh
# =============================================================================
# Installs the CarPi Python application into the image at /opt/carpi.
#
# Uses /opt/carpi (not /home/pi/carpi) because:
#   - /opt is the conventional location for third-party applications on Linux
#   - It's outside the user home directory, so read-only overlayfs doesn't
#     affect it (the app files are part of the immutable lower layer)
#   - The systemd service runs as user 'pi' but from /opt/carpi
# =============================================================================

echo "==> [02-carpi-app] Installing CarPi application"

CARPI_DEST="${ROOTFS_DIR}/opt/carpi"

# ---------------------------------------------------------------------------
# 1. Copy application source files into the image
# ---------------------------------------------------------------------------
install -d "${CARPI_DEST}"

# The app source lives at ../../carpi/ relative to this stage directory.
# In the pi-gen build, STAGE_DIR points to this stage's directory, so:
APP_SRC="$(dirname "$(dirname "${STAGE_DIR}")")/carpi"

if [[ -d "${APP_SRC}" ]]; then
    cp -r "${APP_SRC}/." "${CARPI_DEST}/"
    echo "Copied CarPi source from ${APP_SRC}"
else
    # Fallback: copy from the files/ directory bundled with this stage
    # (used when building from a self-contained pi-gen-config archive)
    cp -r files/carpi/. "${CARPI_DEST}/"
    echo "Copied CarPi source from stage files/"
fi

# Set ownership — app runs as pi user
on_chroot << 'EOF'
chown -R pi:pi /opt/carpi
chmod +x /opt/carpi/main.py
EOF

echo "CarPi installed to /opt/carpi"

# ---------------------------------------------------------------------------
# 2. Install Python dependencies
# ---------------------------------------------------------------------------
# python-obd and flask are not in Debian apt, so we install via pip.
# We install system-wide (not per-user virtualenv) because the systemd
# service runs as user 'pi' but needs access to these packages.
on_chroot << 'EOF'
echo "Installing Python packages: obd flask pywebview"
python3 -m pip install --break-system-packages obd flask pywebview 2>/dev/null \
    || python3 -m pip install obd flask pywebview

echo "Python packages installed:"
python3 -m pip show obd flask pywebview | grep -E "^(Name|Version):"
EOF

# ---------------------------------------------------------------------------
# 3. Create a log directory that survives the read-only root
# ---------------------------------------------------------------------------
# /var/log is writable (it's tmpfs in our read-only setup), but we
# explicitly create the carpi log dir in case tmpfs isn't set up yet.
install -d -m 755 "${ROOTFS_DIR}/var/log/carpi"
on_chroot << 'EOF'
chown pi:pi /var/log/carpi
EOF

echo "==> [02-carpi-app] Application install complete"
