#!/usr/bin/env bash
# =============================================================================
# install.sh - CarPi Full Setup Script
# =============================================================================
# Run this ONCE on a fresh Raspberry Pi OS Lite (64-bit) install.
# Installs all dependencies, configures Bluetooth, WiFi hotspot, and
# sets up the CarPi systemd service for auto-launch on boot.
#
# Usage:
#   cd /home/pi/carpi/setup
#   chmod +x install.sh
#   sudo ./install.sh
#
# After running, edit /home/pi/carpi/config.py to set your OBD2 MAC address.
# =============================================================================

set -e  # Exit on any error

# --- Colors for output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log()  { echo -e "${GREEN}[CarPi]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN] ${NC} $*"; }
err()  { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }
step() { echo -e "\n${BLUE}==> $*${NC}"; }

# --- Require root ---
[[ $EUID -eq 0 ]] || err "Run as root: sudo ./install.sh"

CARPI_DIR="/home/pi/carpi"
CARPI_USER="pi"

# ---------------------------------------------------------------------------
step "1. Updating package lists"
# ---------------------------------------------------------------------------
apt-get update -qq

# ---------------------------------------------------------------------------
step "2. Installing system packages"
# ---------------------------------------------------------------------------
apt-get install -y \
    python3 \
    python3-pip \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libmtdev-dev \
    bluetooth \
    bluez \
    bluez-tools \
    rfcomm \
    hostapd \
    dnsmasq \
    iptables \
    git \
    curl \
    --no-install-recommends

log "System packages installed"

# ---------------------------------------------------------------------------
step "3. Installing Python packages"
# ---------------------------------------------------------------------------
# Use --break-system-packages on newer pip versions (Debian Bookworm+)
PIP_FLAGS="--break-system-packages"
pip3 install $PIP_FLAGS obd flask kivy 2>/dev/null || pip3 install obd flask kivy

log "Python packages installed: obd flask kivy"

# ---------------------------------------------------------------------------
step "4. Configuring Bluetooth"
# ---------------------------------------------------------------------------

# Enable and start Bluetooth service
systemctl enable bluetooth
systemctl start bluetooth || true

# Allow Pi user to use Bluetooth without sudo
if ! groups $CARPI_USER | grep -q bluetooth; then
    usermod -aG bluetooth $CARPI_USER
    log "Added $CARPI_USER to bluetooth group"
fi

# Set Bluetooth adapter to be always-on and auto-enable
cat > /etc/bluetooth/main.conf.carpi << 'EOF'
[Policy]
AutoEnable=true

[General]
Name = CarPi-BT
Class = 0x000100
DiscoverableTimeout = 0
EOF

# Only update if sections don't already exist
if ! grep -q "AutoEnable" /etc/bluetooth/main.conf; then
    cat /etc/bluetooth/main.conf.carpi >> /etc/bluetooth/main.conf
    log "Updated /etc/bluetooth/main.conf"
else
    warn "Bluetooth config already customized — skipping"
fi
rm -f /etc/bluetooth/main.conf.carpi

# Allow rfcomm without sudo — add udev rule
cat > /etc/udev/rules.d/99-rfcomm.rules << 'EOF'
KERNEL=="rfcomm*", MODE="0666"
EOF
log "rfcomm udev rule added"

# ---------------------------------------------------------------------------
step "5. Configuring WiFi Hotspot"
# ---------------------------------------------------------------------------

# Stop conflicting services during setup
systemctl stop hostapd 2>/dev/null || true
systemctl stop dnsmasq 2>/dev/null || true

# Disable wpa_supplicant on wlan0 (we're using it as AP, not client)
# If you need internet, you'd configure a second interface.
systemctl disable wpa_supplicant 2>/dev/null || true
rfkill unblock wifi 2>/dev/null || true

# Static IP for the hotspot interface
WLAN_IFACE="wlan0"
HOTSPOT_IP="192.168.4.1"
DHCP_RANGE_START="192.168.4.2"
DHCP_RANGE_END="192.168.4.50"
HOTSPOT_SSID="CarPi"

# /etc/dhcpcd.conf — set static IP on wlan0
if ! grep -q "interface wlan0" /etc/dhcpcd.conf 2>/dev/null; then
    cat >> /etc/dhcpcd.conf << EOF

# CarPi hotspot static IP
interface wlan0
    static ip_address=${HOTSPOT_IP}/24
    nohook wpa_supplicant
EOF
    log "Static IP configured in /etc/dhcpcd.conf"
else
    warn "dhcpcd wlan0 config already exists — skipping"
fi

# hostapd configuration
cat > /etc/hostapd/hostapd.conf << EOF
# CarPi WiFi Hotspot Configuration
interface=wlan0
driver=nl80211
ssid=${HOTSPOT_SSID}
hw_mode=g
channel=6
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
# Uncomment below to add a password (WPA2):
# wpa=2
# wpa_passphrase=YourPassword
# wpa_key_mgmt=WPA-PSK
# wpa_pairwise=TKIP
# rsn_pairwise=CCMP
EOF
log "hostapd configured: SSID=${HOTSPOT_SSID}"

# Tell hostapd where its config is
sed -i 's|#DAEMON_CONF=.*|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd

# dnsmasq configuration (DHCP server for phone clients)
# Back up original config if it exists
[[ -f /etc/dnsmasq.conf ]] && cp /etc/dnsmasq.conf /etc/dnsmasq.conf.orig

cat > /etc/dnsmasq.conf << EOF
# CarPi dnsmasq configuration
interface=wlan0
dhcp-range=${DHCP_RANGE_START},${DHCP_RANGE_END},255.255.255.0,24h
domain=carpi.local
address=/carpi.local/${HOTSPOT_IP}
bogus-priv
no-resolv
EOF
log "dnsmasq configured (DHCP: ${DHCP_RANGE_START}-${DHCP_RANGE_END})"

# Enable hotspot services
systemctl unmask hostapd
systemctl enable hostapd
systemctl enable dnsmasq
log "hostapd and dnsmasq enabled"

# ---------------------------------------------------------------------------
step "6. Configuring display (HDMI + framebuffer)"
# ---------------------------------------------------------------------------

# Force HDMI output even with no monitor detected at boot
BOOT_CONFIG="/boot/config.txt"
# On Pi OS Bookworm (2023+), config is at /boot/firmware/config.txt
[[ -f /boot/firmware/config.txt ]] && BOOT_CONFIG="/boot/firmware/config.txt"

if ! grep -q "hdmi_force_hotplug" "$BOOT_CONFIG"; then
    cat >> "$BOOT_CONFIG" << EOF

# CarPi display settings
hdmi_force_hotplug=1
hdmi_group=2
hdmi_mode=87
hdmi_cvt=800 480 60 6 0 0 0
hdmi_drive=2
disable_overscan=1
EOF
    log "HDMI display config added to $BOOT_CONFIG"
else
    warn "HDMI config already in $BOOT_CONFIG — skipping"
fi

# Set display environment for Kivy (used by systemd service)
cat > /etc/environment.carpi << 'EOF'
KIVY_BCM_DISPMANX_ID=2
EOF
log "Display environment configured"

# Allow carpi user to access framebuffer
if ! groups $CARPI_USER | grep -q video; then
    usermod -aG video $CARPI_USER
    log "Added $CARPI_USER to video group"
fi

# ---------------------------------------------------------------------------
step "7. Setting up CarPi systemd service"
# ---------------------------------------------------------------------------

# Create the service file
SERVICE_SRC="$CARPI_DIR/setup/autostart.service"
SERVICE_DEST="/etc/systemd/system/carpi.service"

if [[ -f "$SERVICE_SRC" ]]; then
    cp "$SERVICE_SRC" "$SERVICE_DEST"
    log "Installed service: $SERVICE_DEST"
else
    # Write it directly if setup directory isn't found
    warn "autostart.service not found at $SERVICE_SRC — writing directly"
    cat > "$SERVICE_DEST" << EOF
[Unit]
Description=CarPi OBD2 Dashboard
After=network.target bluetooth.target
Wants=bluetooth.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/carpi
ExecStart=/usr/bin/python3 /home/pi/carpi/main.py
Restart=always
RestartSec=5
Environment=SDL_VIDEODRIVER=fbcon
Environment=SDL_FBDEV=/dev/fb0
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF
fi

systemctl daemon-reload
systemctl enable carpi.service
log "CarPi service enabled (will start on next boot)"

# ---------------------------------------------------------------------------
step "8. Optional: Boot speed optimizations"
# ---------------------------------------------------------------------------

# Disable services that slow boot and aren't needed
DISABLE_SERVICES=(
    "avahi-daemon"
    "triggerhappy"
    "rsyslog"
    "dphys-swapfile"
)

for svc in "${DISABLE_SERVICES[@]}"; do
    if systemctl is-enabled "$svc" &>/dev/null; then
        systemctl disable "$svc" 2>/dev/null || true
        log "Disabled: $svc"
    fi
done

# Set GPU memory split — dashboard needs GPU RAM for Kivy OpenGL ES
if ! grep -q "gpu_mem" "$BOOT_CONFIG"; then
    echo "gpu_mem=128" >> "$BOOT_CONFIG"
    log "Set gpu_mem=128"
fi

# ---------------------------------------------------------------------------
step "9. File permissions"
# ---------------------------------------------------------------------------

chown -R $CARPI_USER:$CARPI_USER "$CARPI_DIR"
chmod +x "$CARPI_DIR/main.py"
chmod +x "$CARPI_DIR/setup/hotspot.sh" 2>/dev/null || true

# ---------------------------------------------------------------------------
echo ""
log "============================================================"
log "CarPi installation complete!"
log "============================================================"
echo ""
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo ""
echo "  1. Find your Veepeak adapter's Bluetooth MAC address:"
echo "     Turn on the adapter, then run:  hcitool scan"
echo ""
echo "  2. Edit config.py with your MAC address:"
echo "     nano /home/pi/carpi/config.py"
echo "     Change OBD_MAC = \"AA:BB:CC:DD:EE:FF\" to your actual MAC"
echo ""
echo "  3. Reboot to apply all changes:"
echo "     sudo reboot"
echo ""
echo "  4. After reboot, CarPi will auto-start."
echo "     - HDMI dashboard appears automatically"
echo "     - WiFi hotspot 'CarPi' broadcasts automatically"
echo "     - Connect phone to CarPi and open http://192.168.4.1:5000"
echo ""
echo -e "${YELLOW}TROUBLESHOOTING:${NC}"
echo "  View logs:    sudo journalctl -u carpi -f"
echo "  Start manually: cd /home/pi/carpi && python3 main.py"
echo ""
