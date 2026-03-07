# =============================================================================
# trip.py - Trip Computer
# =============================================================================
# Tracks per-trip statistics: elapsed time, distance driven, average speed,
# and average fuel economy. Resets automatically when the engine turns off
# (RPM drops to None/0 for a sustained period).
#
# Usage:
#   Call trip.update(speed_mph, mpg) every fast poll cycle from obd_reader.
#   Call trip.get_trip() to read the current snapshot.
# =============================================================================

import threading
import time

_lock = threading.Lock()

# How long RPM must be None/0 before we consider the engine "off" and reset
_ENGINE_OFF_SECONDS = 10

_trip = {
    "start_time": None,       # time.time() when trip started
    "distance_mi": 0.0,       # accumulated miles
    "speed_samples": 0,       # count of speed readings (for avg)
    "speed_sum": 0.0,         # sum of speed readings
    "mpg_samples": 0,         # count of MPG readings (for avg)
    "mpg_sum": 0.0,           # sum of MPG readings
    "last_tick": None,        # time.time() of last update() call
    "engine_off_since": None, # when RPM first went to 0/None
}


def update(speed_mph: float | None, mpg: float | None, rpm: int | None):
    """Called every fast poll cycle with current readings."""
    with _lock:
        now = time.time()

        # Detect engine off
        if rpm is None or rpm == 0:
            if _trip["engine_off_since"] is None:
                _trip["engine_off_since"] = now
            elif now - _trip["engine_off_since"] >= _ENGINE_OFF_SECONDS and _trip["start_time"] is not None:
                _reset_locked()
                return
            # Don't accumulate data while engine is off
            _trip["last_tick"] = now
            return
        else:
            _trip["engine_off_since"] = None

        # Start trip on first valid RPM
        if _trip["start_time"] is None:
            _trip["start_time"] = now
            _trip["last_tick"] = now
            return

        # Accumulate distance: speed (mph) * dt (hours)
        dt = now - (_trip["last_tick"] or now)
        if speed_mph is not None and speed_mph > 0 and dt > 0:
            hours = dt / 3600.0
            _trip["distance_mi"] += speed_mph * hours
            _trip["speed_samples"] += 1
            _trip["speed_sum"] += speed_mph

        # Accumulate MPG average
        if mpg is not None and mpg > 0:
            _trip["mpg_samples"] += 1
            _trip["mpg_sum"] += mpg

        _trip["last_tick"] = now


def get_trip() -> dict:
    """Return a snapshot of current trip data."""
    with _lock:
        if _trip["start_time"] is None:
            return {
                "active": False,
                "elapsed_s": 0,
                "distance_mi": 0.0,
                "avg_speed_mph": 0.0,
                "avg_mpg": 0.0,
            }

        elapsed = time.time() - _trip["start_time"]
        avg_speed = _trip["speed_sum"] / _trip["speed_samples"] if _trip["speed_samples"] > 0 else 0.0
        avg_mpg = _trip["mpg_sum"] / _trip["mpg_samples"] if _trip["mpg_samples"] > 0 else 0.0

        return {
            "active": True,
            "elapsed_s": round(elapsed),
            "distance_mi": round(_trip["distance_mi"], 2),
            "avg_speed_mph": round(avg_speed, 1),
            "avg_mpg": round(avg_mpg, 1),
        }


def reset():
    """Manually reset the trip."""
    with _lock:
        _reset_locked()


def _reset_locked():
    """Reset trip state (must be called with _lock held)."""
    _trip["start_time"] = None
    _trip["distance_mi"] = 0.0
    _trip["speed_samples"] = 0
    _trip["speed_sum"] = 0.0
    _trip["mpg_samples"] = 0
    _trip["mpg_sum"] = 0.0
    _trip["last_tick"] = None
    _trip["engine_off_since"] = None
