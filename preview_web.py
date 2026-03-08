#!/usr/bin/env python3
"""
preview_web.py — Run the SignalKit Flask web server with animated sample data.

No hardware required. Run from the repo root:
    python3 preview_web.py

Then open http://localhost:5000 in your browser.
Press Ctrl+C to quit.
"""

import sys
import math
import time
import os

# Point imports at the carpi/ source directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "signalkit"))

import config
config.FULLSCREEN = False
config.WEB_PORT = int(os.environ.get("WEB_PORT", 8050))

# ── Animated sample data ─────────────────────────────────────────────────────
_START = time.time()

def _sample_data() -> dict:
    t = time.time() - _START

    rpm_phase = (t % 20) / 20
    if rpm_phase < 0.4:
        rpm = int(800 + rpm_phase / 0.4 * (5200 - 800))
    elif rpm_phase < 0.6:
        rpm = int(5200 - (rpm_phase - 0.4) / 0.2 * (5200 - 4000))
    else:
        rpm = int(4000 - (rpm_phase - 0.6) / 0.4 * (4000 - 800))

    speed = round(rpm / 6500 * 85 + math.sin(t * 0.3) * 3, 1)
    throttle = round(20 + (rpm - 800) / (6500 - 800) * 70 + math.sin(t) * 5, 1)
    engine_load = round(15 + throttle * 0.7 + math.sin(t * 0.7) * 4, 1)
    coolant = round(82 + math.sin(t * 0.05) * 4, 1)
    battery = round(14.1 + math.sin(t * 0.1) * 0.3, 2)
    iat = round(28 + math.sin(t * 0.03) * 3, 1)
    oil = round(95 + math.sin(t * 0.04) * 5, 1)
    stft1 = round(math.sin(t * 0.2) * 4, 1)
    ltft1 = round(math.sin(t * 0.05) * 2, 1)

    dtcs = []
    if int(t / 15) % 2 == 1:
        dtcs = [{"code": "P0420", "description": "Catalyst System Efficiency Below Threshold (Bank 1)"}]

    return {
        "connected": True,
        "status": "Connected  [PREVIEW MODE]",
        "rpm": rpm,
        "speed": speed,
        "throttle": min(100, max(0, throttle)),
        "engine_load": min(100, max(0, engine_load)),
        "coolant_temp": coolant,
        "battery_voltage": battery,
        "intake_air_temp": iat,
        "oil_temp": oil,
        "short_fuel_trim_1": stft1,
        "long_fuel_trim_1": ltft1,
        "short_fuel_trim_2": None,
        "long_fuel_trim_2": None,
        "dtcs": dtcs,
        "dtc_count": len(dtcs),
        "mil_on": len(dtcs) > 0,
        "last_update": time.time(),
        "poll_errors": 0,
    }

# ── Stub the `obd` package ───────────────────────────────────────────────────
from types import ModuleType
_obd_stub = ModuleType("obd")

class _FakeECU:
    ENGINE = 0

_obd_stub.ECU = _FakeECU()
_obd_stub.OBD = None
_obd_stub.OBDCommand = None
_obd_stub.commands = None
sys.modules["obd"] = _obd_stub

# ── Monkey-patch obd_reader.get_data ─────────────────────────────────────────
import obd_reader
obd_reader.get_data = _sample_data

# ── Run the Flask server ─────────────────────────────────────────────────────
import web_server

print(f"\n  SignalKit Web Preview running at http://localhost:{config.WEB_PORT}")
print(f"  Press Ctrl+C to stop.\n")

web_server.run_server()
