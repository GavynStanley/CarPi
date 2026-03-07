#!/usr/bin/env bash
# =============================================================================
# hotspot.sh - WiFi Hotspot Management Script
# =============================================================================
# Manually start, stop, or check the CarPi WiFi hotspot.
# The hotspot is normally managed by systemd (hostapd + dnsmasq),
# but this script is useful for troubleshooting or manual control.
#
# Usage:
#   sudo ./hotspot.sh start    # Start the hotspot
#   sudo ./hotspot.sh stop     # Stop the hotspot
#   sudo ./hotspot.sh status   # Check status
#   sudo ./hotspot.sh restart  # Restart everything
#
# install.sh sets this up automatically. Only run this manually if you
# need to troubleshoot or re-apply settings.
# =============================================================================

set -e

IFACE="wlan0"
HOTSPOT_IP="192.168.4.1"
HOTSPOT_SSID="CarPi"
DHCP_RANGE="192.168.4.2,192.168.4.50,12h"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log()  { echo -e "${GREEN}[hotspot]${NC} $*"; }
warn() { echo -e "${YELLOW}[hotspot]${NC} $*"; }
err()  { echo -e "${RED}[ERROR]${NC}   $*"; exit 1; }

[[ $EUID -eq 0 ]] || err "Run as root: sudo ./hotspot.sh $*"

cmd_start() {
    log "Starting WiFi hotspot: SSID=$HOTSPOT_SSID on $IFACE"

    # Unblock WiFi
    rfkill unblock wifi 2>/dev/null || true

    # Bring interface up
    ip link set "$IFACE" up

    # Assign static IP
    ip addr flush dev "$IFACE" 2>/dev/null || true
    ip addr add "$HOTSPOT_IP/24" dev "$IFACE"
    log "IP assigned: $HOTSPOT_IP/24 on $IFACE"

    # Start hostapd (access point)
    systemctl start hostapd
    sleep 1

    if systemctl is-active hostapd &>/dev/null; then
        log "hostapd started (WiFi AP broadcasting)"
    else
        warn "hostapd may have failed — check: journalctl -u hostapd -n 20"
    fi

    # Start dnsmasq (DHCP server for phone clients)
    systemctl start dnsmasq
    sleep 1

    if systemctl is-active dnsmasq &>/dev/null; then
        log "dnsmasq started (DHCP server active)"
    else
        warn "dnsmasq may have failed — check: journalctl -u dnsmasq -n 20"
    fi

    log "Hotspot started. Connect phone to '$HOTSPOT_SSID'"
    log "Dashboard URL: http://$HOTSPOT_IP:5000"
}

cmd_stop() {
    log "Stopping WiFi hotspot"
    systemctl stop hostapd 2>/dev/null && log "hostapd stopped" || warn "hostapd was not running"
    systemctl stop dnsmasq 2>/dev/null && log "dnsmasq stopped" || warn "dnsmasq was not running"

    # Remove static IP
    ip addr del "$HOTSPOT_IP/24" dev "$IFACE" 2>/dev/null || true
    log "Hotspot stopped"
}

cmd_status() {
    echo ""
    echo "=== WiFi Hotspot Status ==="
    echo ""

    # Interface info
    echo -n "Interface $IFACE: "
    ip link show "$IFACE" 2>/dev/null | grep -q "UP" && echo -e "${GREEN}UP${NC}" || echo -e "${RED}DOWN${NC}"

    echo -n "IP address:       "
    ip addr show "$IFACE" 2>/dev/null | grep "inet " | awk '{print $2}' || echo "not assigned"

    # hostapd
    echo -n "hostapd:          "
    systemctl is-active hostapd 2>/dev/null && true || echo -e "${RED}inactive${NC}"

    # dnsmasq
    echo -n "dnsmasq:          "
    systemctl is-active dnsmasq 2>/dev/null && true || echo -e "${RED}inactive${NC}"

    # Connected clients
    echo ""
    echo "Connected clients (ARP table for 192.168.4.x):"
    arp -n 2>/dev/null | grep "192.168.4\." || echo "  No clients found"

    # SSID check
    echo ""
    echo -n "Broadcasting SSID: "
    iw dev "$IFACE" info 2>/dev/null | grep ssid | awk '{print $2}' || echo "unknown"

    echo ""
}

cmd_restart() {
    cmd_stop
    sleep 2
    cmd_start
}

# Verify prerequisites
check_deps() {
    for dep in hostapd dnsmasq rfkill ip iw; do
        command -v "$dep" &>/dev/null || err "Missing: $dep (run install.sh first)"
    done
}

# --- Main ---
ACTION="${1:-status}"
check_deps

case "$ACTION" in
    start)   cmd_start   ;;
    stop)    cmd_stop    ;;
    status)  cmd_status  ;;
    restart) cmd_restart ;;
    *)
        echo "Usage: sudo $0 {start|stop|status|restart}"
        exit 1
        ;;
esac
