"""One numeric UTC-clock to SPICE ET conversion for table/bulk state epochs.

Caller must load and verify its chosen leap-seconds kernel before invoking.
Assumes no future leap seconds beyond the chosen LSK's last entry.
"""
from datetime import datetime, timezone

UTC_J2000_CLOCK = datetime(2000, 1, 1, 12, tzinfo=timezone.utc)


def utc_epochs_to_et(epochs, *, deltet):
    """Map UTC datetime ticks to ET with one shared arithmetic path."""
    out = []
    for tick in epochs:
        if tick.tzinfo is None or tick.utcoffset().total_seconds() != 0:
            raise ValueError('UTC-aware epoch required')
        utc_seconds = (tick - UTC_J2000_CLOCK).total_seconds()
        out.append(utc_seconds + deltet(utc_seconds, 'UTC'))
    return out
