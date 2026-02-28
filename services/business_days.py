from __future__ import annotations

from datetime import date, timedelta


def ph_holidays(year: int) -> set[date]:
    """Philippine regular holidays (fixed-date). Expand as needed."""
    return {
        date(year, 1, 1),    # New Year's Day
        date(year, 4, 9),    # Araw ng Kagitingan
        date(year, 5, 1),    # Labor Day
        date(year, 6, 12),   # Independence Day
        date(year, 8, 25),   # National Heroes Day (approx)
        date(year, 11, 30),  # Bonifacio Day
        date(year, 12, 25),  # Christmas Day
        date(year, 12, 30),  # Rizal Day
    }


def next_business_day(d: date | None = None) -> date:
    """Return *d* if it is a weekday and not a PH holiday, else the next one."""
    if d is None:
        d = date.today()
    holidays = ph_holidays(d.year) | ph_holidays(d.year + 1)
    while d.weekday() >= 5 or d in holidays:
        d += timedelta(days=1)
    return d
