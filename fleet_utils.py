# fleet_utils.py
# Helpers for the KM-Waechter nightly run.
# Cleaned up: dead functions removed, wrong km-to-miles constant fixed.

MILES_PER_KM = 0.621371   # correct: 1 km = 0.621371 miles (was 1.609, which is km-per-mile)


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles. Used by the nightly UK partner report."""
    return km * MILES_PER_KM


def format_number(value: float) -> str:
    """Format a float to one decimal place."""
    return f"{value:.1f}"
