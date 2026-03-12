#!/bin/sh
# Detect the correct DRM card for Qt EGLFS on Raspberry Pi 5.
# Pi 5 exposes HDMI on card1 (card0 is the V3D render-only GPU).
# Writes a JSON config file that Qt EGLFS reads for the device path.

for card in /dev/dri/card*; do
    if udevadm info -q property "$card" 2>/dev/null | grep -q "ID_PATH.*platform.*gpu"; then
        echo '{"device":"'"$card"'"}' > /tmp/signalkit-kms.json
        exit 0
    fi
done

# Fallback — let Qt auto-detect
echo '{}' > /tmp/signalkit-kms.json
