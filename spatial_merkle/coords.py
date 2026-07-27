"""Fixed-point lon/lat coordinates (MVP contract §1)."""

from __future__ import annotations

from dataclasses import dataclass

COORD_SCALE = 10_000_000


@dataclass(frozen=True, order=True)
class Point:
    """Quantized point (lon_q, lat_q) as signed integers."""

    x: int
    y: int

    def to_tuple(self) -> tuple[int, int]:
        return (self.x, self.y)


def quantize(lon_deg: float, lat_deg: float) -> Point:
    return Point(round(lon_deg * COORD_SCALE), round(lat_deg * COORD_SCALE))


def dequantize(p: Point) -> tuple[float, float]:
    return (p.x / COORD_SCALE, p.y / COORD_SCALE)
