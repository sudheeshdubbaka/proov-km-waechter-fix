# km_wachter.py
# KM-Waechter decides when a Vossberg Mobility car needs a service.
# Written in 2013. Modernized style; bugs fixed.

SERVICE_INTERVAL_KM = 15000
WARN_AT_PERCENT = 80


def wear_percent(km_since_service: float, interval: float) -> float:
    """Return how many percent of the service interval has been used up.

    Uses float division so a car at 14,900 of 15,000 km reports ~99.3 %,
    not 0 % (the old integer-floor bug).
    """
    return (km_since_service / interval) * 100


def needs_service(car: dict) -> bool:
    """Return True if the car has used at least WARN_AT_PERCENT of its interval.

    If last_service_km is absent (no reading on file) the car is not flagged —
    unknown history is not the same as zero km since the last service.
    """
    last = car.get("last_service_km", None)
    if last is None:
        return False
    km_since = car["odometer"] - last
    return wear_percent(km_since, SERVICE_INTERVAL_KM) >= WARN_AT_PERCENT


def check_fleet(fleet: list[dict]) -> list:
    """Flag every car that needs a service and return their IDs."""
    flagged = []
    for car in fleet:
        if needs_service(car):
            flagged.append(car["id"])
            print(f"SERVICE DUE: {car['id']}")
    return flagged
