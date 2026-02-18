from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any

DEFAULT_USER_AGENT = "ECO-TRACK Bayawan CENRO Office (development) - Django reverse geocoder"


def reverse_geocode_osm(lat: float, lon: float, timeout: int = 10) -> dict[str, Any] | None:
    params = {
        "format": "jsonv2",
        "lat": f"{lat:.6f}",
        "lon": f"{lon:.6f}",
        "addressdetails": "1",
    }
    url = "https://nominatim.openstreetmap.org/reverse?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "application/json",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except Exception:
        return None


def address_in_bayawan(addr: dict[str, Any], display_name: str | None) -> bool:
    parts = [
        display_name or "",
        addr.get("city"),
        addr.get("town"),
        addr.get("municipality"),
        addr.get("county"),
        addr.get("province"),
        addr.get("state"),
        addr.get("region"),
        addr.get("island"),
    ]
    hay = " ".join([p for p in parts if p]).lower()
    return "bayawan" in hay


def extract_barangay(addr: dict[str, Any]) -> str | None:
    for key in ("suburb", "village", "hamlet", "neighbourhood"):
        val = addr.get(key)
        if val:
            return str(val)
    return None
