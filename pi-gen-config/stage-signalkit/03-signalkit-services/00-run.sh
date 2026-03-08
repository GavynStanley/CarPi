#!/bin/bash -e
# =============================================================================
# 03-signalkit-services/00-run.sh
# =============================================================================
# Installs and enables the signalkit.service systemd unit.
# This is what makes SignalKit auto-start on every boot with no user interaction.
# =============================================================================

echo "==> [03-signalkit-services] Installing systemd service"

# Install the service unit file
install -m 644 files/signalkit.service "${ROOTFS_DIR}/etc/systemd/system/signalkit.service"

# Enable it so it starts on boot (equivalent to 'systemctl enable signalkit')
# In pi-gen chroot, systemctl enable works via symlinks in /etc/systemd/system/
on_chroot << 'EOF'
systemctl enable signalkit.service
echo "signalkit.service enabled"
EOF

# ---------------------------------------------------------------------------
# X11 display server service
# ---------------------------------------------------------------------------
# pywebview uses GTK + WebKit which requires X11. This minimal Xorg service
# starts a framebuffer-only X server with no window manager — SignalKit renders
# fullscreen via pywebview on top of it.
install -m 644 files/signalkit-x11.service \
    "${ROOTFS_DIR}/etc/systemd/system/signalkit-x11.service"

on_chroot << 'EOF'
systemctl enable signalkit-x11.service
echo "signalkit-x11.service enabled"
EOF

# Allow pi user to start X without root
install -d "${ROOTFS_DIR}/etc/X11"
cat > "${ROOTFS_DIR}/etc/X11/Xwrapper.config" << 'EOF'
allowed_users=anybody
needs_root_rights=yes
EOF

# ---------------------------------------------------------------------------
# Bluetooth rfcomm bind helper service
# ---------------------------------------------------------------------------
# rfcomm bind must be run each boot before the signalkit app starts.
# We create a oneshot service that does this, ordered before signalkit.service.
install -m 644 files/signalkit-rfcomm.service \
    "${ROOTFS_DIR}/etc/systemd/system/signalkit-rfcomm.service"

on_chroot << 'EOF'
systemctl enable signalkit-rfcomm.service
echo "signalkit-rfcomm.service enabled"
EOF

# ---------------------------------------------------------------------------
# WiFi hotspot configuration service
# ---------------------------------------------------------------------------
# Regenerates hostapd.conf from config.py on each boot so WiFi SSID/password
# changes made via the web UI take effect.
install -m 644 files/signalkit-wifi.service \
    "${ROOTFS_DIR}/etc/systemd/system/signalkit-wifi.service"

# Helper script that generates hostapd.conf from config.py
install -d "${ROOTFS_DIR}/opt/signalkit/scripts"
install -m 755 files/signalkit-gen-hostapd.sh \
    "${ROOTFS_DIR}/opt/signalkit/scripts/signalkit-gen-hostapd.sh"

on_chroot << 'EOF'
systemctl enable signalkit-wifi.service
echo "signalkit-wifi.service enabled"
EOF

echo "==> [03-signalkit-services] Services installed"
