#!/bin/bash
# Hotfix: push local code changes to Pi over SSH
# Usage: bash hotfix.sh

PI="pi@169.254.100.2"
PASS="signalkit"
REMOTE="/opt/signalkit"

# Remount root as read-write (overlayfs)
echo "Remounting root as read-write..."
sshpass -p "$PASS" ssh "$PI" "sudo mount -o remount,rw /" 2>/dev/null

# Copy updated Python files
echo "Copying updated files..."
for f in signalkit/web_server.py signalkit/display.py signalkit/main.py signalkit/config.py signalkit/bt_pan.py; do
    echo "  $f"
    sshpass -p "$PASS" scp "$f" "$PI:$REMOTE/$f"
done

# Copy updated service files
echo "Copying service files..."
for s in signalkit-x11.service signalkit-rfcomm.service; do
    echo "  $s"
    sshpass -p "$PASS" scp "pi-gen-config/stage-signalkit/03-signalkit-services/files/$s" "$PI:/tmp/$s"
    sshpass -p "$PASS" ssh "$PI" "sudo cp /tmp/$s /etc/systemd/system/$s"
done

# Reload systemd and restart services
echo "Restarting services..."
sshpass -p "$PASS" ssh "$PI" "sudo systemctl daemon-reload && sudo systemctl restart signalkit-x11 && sleep 2 && sudo systemctl restart signalkit"

echo "Done! Changes applied."
