"""Interview-derived (stylised, pseudonymised) space-time profiles."""
from typing import Dict, List

import yaml

from . import config


def load_profiles(path=config.PROFILES_FILE) -> Dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def crossing_speed_kmh(distance_km: float, minutes: float) -> float:
    """Average speed over a segment, e.g. the 1.06 km Causeway crossed in 60-90 minutes."""
    if minutes <= 0:
        raise ValueError("minutes must be positive")
    return distance_km / (minutes / 60.0)


def segments(waypoints: List) -> List[Dict]:
    """Consecutive (node, hour) pairs as segments with duration in minutes."""
    out = []
    for (n1, t1), (n2, t2) in zip(waypoints[:-1], waypoints[1:]):
        out.append({"from": n1, "to": n2, "t0": t1, "t1": t2, "minutes": round((t2 - t1) * 60),
                    "stationary": n1 == n2})
    return out


def time_colour(minutes: float) -> str:
    """Travel-time colour ramp (green < 10 min ... crimson > 60 min)."""
    t = max(1, min(minutes, 100))
    stops = [(1, (0, 160, 80)), (10, (80, 200, 50)), (20, (200, 210, 0)), (30, (240, 160, 0)),
             (45, (240, 80, 0)), (60, (220, 30, 0)), (100, (160, 5, 5))]
    for (a, ca), (b, cb) in zip(stops[:-1], stops[1:]):
        if t <= b:
            f = (t - a) / (b - a)
            r, g, bl = (int(ca[i] + f * (cb[i] - ca[i])) for i in range(3))
            return f"#{r:02x}{g:02x}{bl:02x}"
    return "#a00505"
