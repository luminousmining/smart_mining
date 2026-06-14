import math


def _is_nan_or_negative(value) -> bool:
    if value is None:
        return False
    try:
        f = float(value)
        return math.isnan(f) or f < 0
    except (TypeError, ValueError):
        return True
