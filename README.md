# CarPi OS — Custom Raspberry Pi OBD2 Dashboard

A **custom Linux OS image** built with pi-gen that boots directly into a car dashboard — no desktop, no login, no setup. Flash the `.img` to an SD card and it works.

Built for the Raspberry Pi Zero 2 W with a 800x480 HDMI display and a Veepeak Bluetooth OBD2 adapter.

**Target vehicle:** 2021 Kia Forte (1.8L MPI)

---

## What makes this a custom OS (not just an app)

- Built with **pi-gen** — the same tool used to build official Raspberry Pi OS
- The dashboard, Bluetooth config, WiFi hotspot, and systemd services are all **baked into the image at build time**
- **Read-only root filesystem** (overlayfs) — survives hard power cuts with no SD card corruption
- **No desktop environment**, no login prompt, no unnecessary services
- Boot directly from power-on to dashboard in ~15 seconds
- Flash once, use forever — the SD card is never written to during normal operation

---

## Features

- Full-screen HDMI dashboard (pygame) — RPM, speed, coolant temp, battery voltage, throttle %, engine load, intake air temp, oil temp (Kia extended PID), fuel trim, active DTCs
- Overheat and low battery warnings with color alerts
- Mobile web dashboard — connect phone to Pi's hotspot, open browser
- Bluetooth auto-pair and reconnect to OBD2 adapter on boot
- WiFi hotspot broadcasts automatically (SSID: CarPi)
- Read-only filesystem via overlayfs — power-cut safe

---

## Hardware

| Component | Part |
|-----------|------|
| SBC | Raspberry Pi Zero 2 W |
| Display | 800x480 HDMI LCD (mounted in dash) |
| OBD2 Adapter | Veepeak BT/BLE ELM327 |
| Power | Car 12V to USB-C (5V 3A minimum) |

---

## Project Structure

```
build.sh                         # Main build script — run this to produce the .img
pi-gen-config/
├── config                       # pi-gen build settings (arch, user, locale)
└── stage-carpi/                 # Custom OS stage baked into the image
    ├── 00-carpi-packages/
    │   └── 00-packages          # apt packages to install
    ├── 01-carpi-system/
    │   ├── 00-run.sh            # Bluetooth, hotspot, display, boot config
    │   └── files/               # Config files written into the image
    │       ├── bluetooth-main.conf
    │       ├── hostapd.conf
    │       └── dnsmasq.conf
    ├── 02-carpi-app/
    │   └── 00-run.sh            # Copies carpi/ into /opt/carpi, installs pip deps
    ├── 03-carpi-services/
    │   ├── 00-run.sh            # Enables systemd services
    │   └── files/
    │       ├── carpi.service    # Main dashboard service
    │       └── carpi-rfcomm.service  # Bluetooth serial bind (runs before carpi)
    └── 04-carpi-readonly/
        └── 00-run.sh            # Enables overlayfs read-only root

carpi/                           # The dashboard application (baked into image)
├── main.py
├── obd_reader.py
├── display.py
├── web_server.py
├── config.py                    # Edit OBD_MAC here before building
├── dtc_descriptions.py
└── setup/                       # Alternative: manual install scripts (if not building image)
    ├── install.sh
    ├── autostart.service
    └── hotspot.sh
```

---

## Building the OS Image

This is the primary workflow. `build.sh` clones pi-gen, links the custom stage, and produces a flashable `.img`.

### Requirements

| Requirement | Notes |
|-------------|-------|
| Linux host | Ubuntu 22.04+ recommended. macOS needs `--docker`. |
| ~8 GB free disk space | For build artifacts |
| Internet access | Downloads Debian packages during build |
| Docker (optional) | Required for macOS; optional on Linux |

### Step 1 — Set your OBD2 MAC address

**Do this before building** so it's baked into the image.

Find your Veepeak adapter's MAC by temporarily connecting another device:
```bash
# On any Linux machine with Bluetooth:
hcitool scan
# Output: AA:BB:CC:DD:EE:FF    VEEPEAK-OBD
```

Then edit [carpi/config.py](carpi/config.py):
```python
OBD_MAC = "AA:BB:CC:DD:EE:FF"   # ← replace with your actual MAC
```

### Step 2 — Install build dependencies (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y \
    coreutils quilt parted \
    qemu-user-static qemu-user-binfmt \
    debootstrap zerofree \
    zip dosfstools libarchive-tools libcap2-bin \
    grep rsync xz-utils pigz arch-test \
    --no-install-recommends
```

`build.sh` will also run this automatically if any package is missing, so you can skip this step and let the script handle it.

### Step 3 — Build

**On Linux (native, fastest):**
```bash
chmod +x build.sh
./build.sh
```

**On macOS or Windows (via Docker):**
```bash
./build.sh --docker
```

Build takes **20–60 minutes** depending on your machine and internet speed.

Output: `deploy/CarPi-YYYY-MM-DD.img.zip`

### Step 4 — Flash to SD card

**Using Raspberry Pi Imager (easiest):**
1. Open Raspberry Pi Imager
2. Choose OS → Use Custom → select the `.img.zip` from `deploy/`
3. Flash to your microSD card

**Using `dd` on Linux:**
```bash
unzip -p deploy/CarPi-*.img.zip | sudo dd of=/dev/sdX bs=4M status=progress
# Replace /dev/sdX with your SD card device (check with lsblk)
```

### Step 5 — Install and power on

Insert the SD card into the Pi Zero 2 W and apply power. That's it.

- HDMI dashboard appears in ~15 seconds
- `CarPi` WiFi hotspot starts automatically
- Connect phone → open `http://192.168.4.1:5000`

---

## Changing the OBD2 MAC After Flashing

If you need to update the MAC without rebuilding the image:

```bash
# 1. Temporarily disable the read-only filesystem
sudo raspi-config nonint do_overlayfs 1   # 1 = disable

# 2. Reboot into read-write mode
sudo reboot

# 3. Edit the config
nano /opt/carpi/config.py

# 4. Re-enable read-only filesystem
sudo raspi-config nonint do_overlayfs 0   # 0 = enable

# 5. Reboot
sudo reboot
```

---

## Using the Dashboard

### HDMI Display

The dashboard auto-starts 5–10 seconds after power-on (depending on Bluetooth connection speed).

| Section | Data shown |
|---------|-----------|
| Top-left (large) | RPM with color bar |
| Top-right (large) | Speed (MPH) + Throttle % |
| Middle row | Coolant temp, Battery V, Engine Load, Check Engine |
| Lower row | Intake Air Temp, Oil Temp, Fuel Trim B1 |
| Bottom | Active DTC codes with descriptions |

**Warning colors:**
- Green = normal
- Amber = caution
- Red = warning / action needed

### Phone Web UI

1. Connect your phone to the **CarPi** WiFi network (no password)
2. Open your browser to: `http://192.168.4.1:5000`
3. The dashboard auto-updates every second

---

## Configuration

Edit `/home/pi/carpi/config.py` to customize:

```python
OBD_MAC = "AA:BB:CC:DD:EE:FF"  # Your adapter's MAC — REQUIRED
RPM_REDLINE = 6500               # Redline for RPM bar
COOLANT_OVERHEAT_C = 105         # Overheat warning threshold (°C)
BATTERY_LOW_V = 12.0             # Low battery warning (V)
SCREEN_WIDTH = 800               # Display resolution
SCREEN_HEIGHT = 480
FULLSCREEN = True
```

---

## Troubleshooting

### Dashboard doesn't start

```bash
sudo journalctl -u carpi -f        # Follow live logs
sudo systemctl status carpi        # Check service status
cd /home/pi/carpi && python3 main.py  # Run manually to see errors
```

### Bluetooth won't connect

```bash
# Check if adapter is visible
hcitool scan

# Try pairing manually
bluetoothctl
> power on
> scan on
> pair AA:BB:CC:DD:EE:FF
> trust AA:BB:CC:DD:EE:FF
> quit

# Bind rfcomm manually
sudo rfcomm bind /dev/rfcomm0 AA:BB:CC:DD:EE:FF 1

# Test OBD connection
python3 -c "import obd; c = obd.OBD('/dev/rfcomm0'); print(c.status())"
```

### WiFi hotspot not appearing

```bash
sudo systemctl status hostapd
sudo journalctl -u hostapd -n 30
sudo ./setup/hotspot.sh status
sudo ./setup/hotspot.sh restart
```

### Display shows nothing / wrong resolution

```bash
# Check the boot config has the right resolution
cat /boot/firmware/config.txt | grep hdmi

# Verify pygame can open display
export SDL_VIDEODRIVER=fbcon SDL_FBDEV=/dev/fb0
python3 -c "import pygame; pygame.init(); s = pygame.display.set_mode((800,480)); print('OK')"
```

### Oil temp shows "N/A"

This is expected on many Kia Forte trims. The oil temperature PID (`mode 22, 0x2101`) is a Kia/Hyundai extended PID that may not be supported on the base trim or US market ECU. The app tries it and falls back gracefully if unsupported.

### Check engine codes shown but no description

Add the code and its description to the `DTC_CODES` dict in `dtc_descriptions.py`.

---

## Read-Only Filesystem (Optional)

To protect the microSD card from power-cut corruption, you can enable overlayfs:

```bash
sudo raspi-config
# Advanced Options > Overlay File System > Yes
```

**Note:** With overlayfs enabled, changes (including config.py edits) won't persist after reboot. Disable it, make changes, then re-enable.

---

## Boot Time Optimization

Current typical boot time: **12–18 seconds** from power-on to dashboard visible.

The install script disables several non-essential services. For further optimization:

```bash
# Analyze boot time
systemd-analyze blame | head -20

# Disable more services you don't need
sudo systemctl disable ModemManager
sudo systemctl disable hciuart   # Only if not using UART Bluetooth
```

---

## Development Notes

### OBD2 Polling Architecture

- `OBDReader` runs in a background thread (`threading.Thread`)
- All data stored in a shared `_data` dict protected by `threading.Lock`
- Fast data (RPM, speed): polled every ~1 second
- Slow data (temps, voltage, DTCs): polled every ~5 seconds
- `obd_reader.get_data()` returns a thread-safe snapshot

### Bluetooth / rfcomm

The Veepeak adapter uses classic Bluetooth SPP (Serial Port Profile), not true BLE, despite the "BLE" marketing. python-OBD communicates over `/dev/rfcomm0`, which is a virtual serial port created by the BlueZ `rfcomm bind` command.

If you have a true BLE-only adapter, you'll need a different library (e.g., `bleak`) and significant changes to `obd_reader.py`.

### Kia Extended PIDs

Kia/Hyundai vehicles use OBD2 service `0x22` for manufacturer-specific data. The oil temperature PID `2101` returns a response where byte index 7 contains the raw temperature value. Formula: `temp_c = (byte_value * 0.75) - 48`. These are configurable in `config.py`.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `python-OBD` | OBD2 communication over rfcomm |
| `pygame` | HDMI display rendering |
| `flask` | Web server for phone UI |
| `bluez` | Bluetooth stack |
| `hostapd` | WiFi access point |
| `dnsmasq` | DHCP server for hotspot clients |
| `rfcomm` | Bluetooth serial port binding |

Install everything: `sudo ./setup/install.sh`

---

## License

MIT — do whatever you want with it.
