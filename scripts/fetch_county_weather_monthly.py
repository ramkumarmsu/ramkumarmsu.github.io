#!/usr/bin/env python3
"""
Fetch monthly-average weather features for counties in county_list.csv.

Period: 2026-04-01 through 2026-06-30
Sources:
  - Open-Meteo Historical Forecast API (ECMWF IFS 0.25°) for meteorological fields
  - NOAA PSL EDDI CONUS archive (EDDI_ETrs_03mn / EDDI_ETrs_06wk) for drought indices

Specific humidity (q850, q250) is derived from temperature and relative humidity
at the corresponding pressure level.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

FEATURES = [
    "t2m",
    "t850",
    "EDDI_ETrs_03m",
    "t250",
    "q250",
    "tmax",
    "r500",
    "u850",
    "u250",
    "v500",
    "r850",
    "r250",
    "v250",
    "q850",
    "v850",
    "u10",
    "v10",
    "d2m",
    "sp",
    "SRO",
    "EDDI_ETrs_06wk",
    "tp",
]

OPEN_METEO_HOURLY = [
    "temperature_2m",
    "dew_point_2m",
    "surface_pressure",
    "precipitation",
    "runoff",
    "temperature_850hPa",
    "temperature_250hPa",
    "relative_humidity_850hPa",
    "relative_humidity_250hPa",
    "relative_humidity_500hPa",
    "wind_u_component_10m",
    "wind_v_component_10m",
    "wind_u_component_850hPa",
    "wind_v_component_850hPa",
    "wind_u_component_250hPa",
    "wind_v_component_250hPa",
    "wind_v_component_500hPa",
]

OPEN_METEO_DAILY = ["temperature_2m_max"]

EDDI_SCALE_MAP = {
    "EDDI_ETrs_03m": "03mn",
    "EDDI_ETrs_06wk": "06wk",
}

EDDI_BASE = "https://downloads.psl.noaa.gov/Projects/EDDI/CONUS_archive/data"
OPEN_METEO_URL = "https://historical-forecast-api.open-meteo.com/v1/forecast"


def daterange(start: date, end: date) -> Iterable[date]:
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


def month_windows(start: date, end: date) -> List[Tuple[int, int, date, date]]:
    """Return list of (year, month, month_start, month_end) clipped to [start, end]."""
    windows = []
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        ms = date(y, m, 1)
        if m == 12:
            me = date(y, 12, 31)
        else:
            me = date(y, m + 1, 1) - timedelta(days=1)
        ms = max(ms, start)
        me = min(me, end)
        windows.append((y, m, ms, me))
        if m == 12:
            y, m = y + 1, 1
        else:
            m += 1
    return windows


def specific_humidity(temp_c: np.ndarray, rh_pct: np.ndarray, pressure_hpa: float) -> np.ndarray:
    """Compute specific humidity (kg/kg) from T (°C), RH (%), and pressure (hPa)."""
    es = 6.112 * np.exp((17.67 * temp_c) / (temp_c + 243.5))
    e = (rh_pct / 100.0) * es
    denom = pressure_hpa - 0.378 * e
    with np.errstate(divide="ignore", invalid="ignore"):
        q = 0.622 * e / denom
    return q


def mean_ignore_nan(arr: np.ndarray) -> float:
    if arr.size == 0 or np.all(np.isnan(arr)):
        return float("nan")
    return float(np.nanmean(arr))


def daily_sums_from_hourly(times: Sequence[str], values: Sequence[Optional[float]]) -> Dict[str, float]:
    buckets: Dict[str, List[float]] = defaultdict(list)
    for t, v in zip(times, values):
        if v is None:
            continue
        buckets[t[:10]].append(float(v))
    return {d: float(np.sum(vals)) for d, vals in buckets.items() if vals}


def daily_means_from_hourly(times: Sequence[str], values: Sequence[Optional[float]]) -> Dict[str, float]:
    buckets: Dict[str, List[float]] = defaultdict(list)
    for t, v in zip(times, values):
        if v is None:
            continue
        buckets[t[:10]].append(float(v))
    return {d: float(np.mean(vals)) for d, vals in buckets.items() if vals}


def http_get_json(url: str, retries: int = 6, timeout: int = 300) -> object:
    last_err: Optional[Exception] = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "county-weather-monthly/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - retry broadly for flaky APIs
            last_err = exc
            sleep_s = min(2 ** attempt, 60)
            print(f"  retry {attempt + 1}/{retries} after error: {exc} (sleep {sleep_s}s)", flush=True)
            time.sleep(sleep_s)
    raise RuntimeError(f"Failed GET {url}") from last_err


def http_get_bytes(url: str, retries: int = 6, timeout: int = 300) -> bytes:
    last_err: Optional[Exception] = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "county-weather-monthly/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            sleep_s = min(2 ** attempt, 60)
            print(f"  retry {attempt + 1}/{retries} after error: {exc} (sleep {sleep_s}s)", flush=True)
            time.sleep(sleep_s)
    raise RuntimeError(f"Failed GET {url}") from last_err


def parse_asc(content: bytes) -> Tuple[dict, np.ndarray]:
    text = content.decode("utf-8", errors="ignore")
    lines = text.splitlines()
    meta = {}
    for i in range(6):
        parts = lines[i].split()
        key = parts[0].lower()
        meta[key] = float(parts[1]) if key != "ncols" and key != "nrows" else int(float(parts[1]))
    data = np.loadtxt(lines[6:], dtype=np.float64)
    expected = (meta["nrows"], meta["ncols"])
    if data.shape != expected:
        data = data.reshape(expected)
    return meta, data


def sample_asc(meta: dict, grid: np.ndarray, lats: np.ndarray, lons: np.ndarray) -> np.ndarray:
    ncols = meta["ncols"]
    nrows = meta["nrows"]
    xll = meta["xllcorner"]
    yll = meta["yllcorner"]
    cell = meta["cellsize"]
    nodata = meta.get("nodata_value", -9999.0)
    yur = yll + nrows * cell

    cols = np.floor((lons - xll) / cell).astype(int)
    rows = np.floor((yur - lats) / cell).astype(int)
    out = np.full(lats.shape, np.nan, dtype=np.float64)
    valid = (cols >= 0) & (cols < ncols) & (rows >= 0) & (rows < nrows)
    vals = grid[rows[valid], cols[valid]]
    vals = np.where(vals == nodata, np.nan, vals)
    out[valid] = vals
    return out


def load_counties(path: Path) -> List[dict]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["Latitude"] = float(r["Latitude"])
        r["Longitude"] = float(r["Longitude"])
    return rows


def fetch_open_meteo_batch(
    lats: Sequence[float],
    lons: Sequence[float],
    start: date,
    end: date,
) -> List[dict]:
    params = {
        "latitude": ",".join(f"{x:.6f}" for x in lats),
        "longitude": ",".join(f"{x:.6f}" for x in lons),
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "hourly": ",".join(OPEN_METEO_HOURLY),
        "daily": ",".join(OPEN_METEO_DAILY),
        "models": "ecmwf_ifs025",
        "wind_speed_unit": "ms",
        "timezone": "GMT",
    }
    url = OPEN_METEO_URL + "?" + urllib.parse.urlencode(params)
    payload = http_get_json(url)
    if isinstance(payload, dict):
        if payload.get("error"):
            raise RuntimeError(payload.get("reason", "Open-Meteo error"))
        return [payload]
    return payload


def aggregate_location_month(loc_payload: dict) -> dict:
    hourly = loc_payload["hourly"]
    daily = loc_payload["daily"]
    times = hourly["time"]

    t2m = np.array(hourly["temperature_2m"], dtype=float)
    d2m = np.array(hourly["dew_point_2m"], dtype=float)
    sp = np.array(hourly["surface_pressure"], dtype=float)
    t850 = np.array(hourly["temperature_850hPa"], dtype=float)
    t250 = np.array(hourly["temperature_250hPa"], dtype=float)
    r850 = np.array(hourly["relative_humidity_850hPa"], dtype=float)
    r250 = np.array(hourly["relative_humidity_250hPa"], dtype=float)
    r500 = np.array(hourly["relative_humidity_500hPa"], dtype=float)
    u10 = np.array(hourly["wind_u_component_10m"], dtype=float)
    v10 = np.array(hourly["wind_v_component_10m"], dtype=float)
    u850 = np.array(hourly["wind_u_component_850hPa"], dtype=float)
    v850 = np.array(hourly["wind_v_component_850hPa"], dtype=float)
    u250 = np.array(hourly["wind_u_component_250hPa"], dtype=float)
    v250 = np.array(hourly["wind_v_component_250hPa"], dtype=float)
    v500 = np.array(hourly["wind_v_component_500hPa"], dtype=float)

    q850 = specific_humidity(t850, r850, 850.0)
    q250 = specific_humidity(t250, r250, 250.0)

    precip_daily = daily_sums_from_hourly(times, hourly["precipitation"])
    runoff_daily = daily_sums_from_hourly(times, hourly["runoff"])
    tmax_vals = [v for v in daily["temperature_2m_max"] if v is not None]

    return {
        "t2m": mean_ignore_nan(t2m),
        "t850": mean_ignore_nan(t850),
        "t250": mean_ignore_nan(t250),
        "q250": mean_ignore_nan(q250),
        "q850": mean_ignore_nan(q850),
        "tmax": float(np.mean(tmax_vals)) if tmax_vals else float("nan"),
        "r500": mean_ignore_nan(r500),
        "r850": mean_ignore_nan(r850),
        "r250": mean_ignore_nan(r250),
        "u850": mean_ignore_nan(u850),
        "u250": mean_ignore_nan(u250),
        "v500": mean_ignore_nan(v500),
        "v250": mean_ignore_nan(v250),
        "v850": mean_ignore_nan(v850),
        "u10": mean_ignore_nan(u10),
        "v10": mean_ignore_nan(v10),
        "d2m": mean_ignore_nan(d2m),
        "sp": mean_ignore_nan(sp),
        "SRO": float(np.mean(list(runoff_daily.values()))) if runoff_daily else float("nan"),
        "tp": float(np.mean(list(precip_daily.values()))) if precip_daily else float("nan"),
    }


def fetch_weather_for_month(
    counties: List[dict],
    year: int,
    month: int,
    start: date,
    end: date,
    batch_size: int,
    cache_dir: Path,
) -> Dict[str, dict]:
    cache_path = cache_dir / f"weather_{year}{month:02d}.json"
    if cache_path.exists():
        print(f"Loading weather cache {cache_path}", flush=True)
        with cache_path.open() as f:
            return json.load(f)

    results: Dict[str, dict] = {}
    n = len(counties)
    for i in range(0, n, batch_size):
        batch = counties[i : i + batch_size]
        print(
            f"  Open-Meteo {year}-{month:02d} counties {i + 1}-{i + len(batch)}/{n}",
            flush=True,
        )
        payloads = fetch_open_meteo_batch(
            [c["Latitude"] for c in batch],
            [c["Longitude"] for c in batch],
            start,
            end,
        )
        if len(payloads) != len(batch):
            raise RuntimeError(f"Expected {len(batch)} payloads, got {len(payloads)}")
        for county, payload in zip(batch, payloads):
            results[county["COUNTY_MUNI_CODE"]] = aggregate_location_month(payload)
        # be polite to the free API
        time.sleep(0.4)

    with cache_path.open("w") as f:
        json.dump(results, f)
    return results


def eddi_url(scale: str, day: date) -> str:
    return f"{EDDI_BASE}/{day.year}/EDDI_ETrs_{scale}_{day.strftime('%Y%m%d')}.asc"


def fetch_eddi_month(
    counties: List[dict],
    feature: str,
    year: int,
    month: int,
    start: date,
    end: date,
    cache_dir: Path,
    workers: int = 8,
) -> Dict[str, float]:
    scale = EDDI_SCALE_MAP[feature]
    cache_path = cache_dir / f"eddi_{scale}_{year}{month:02d}.json"
    if cache_path.exists():
        print(f"Loading EDDI cache {cache_path}", flush=True)
        with cache_path.open() as f:
            return json.load(f)

    lats = np.array([c["Latitude"] for c in counties], dtype=float)
    lons = np.array([c["Longitude"] for c in counties], dtype=float)
    codes = [c["COUNTY_MUNI_CODE"] for c in counties]
    days = list(daterange(start, end))

    sums = np.zeros(len(counties), dtype=float)
    counts = np.zeros(len(counties), dtype=float)

    def one_day(day: date) -> Tuple[date, np.ndarray]:
        url = eddi_url(scale, day)
        content = http_get_bytes(url)
        meta, grid = parse_asc(content)
        return day, sample_asc(meta, grid, lats, lons)

    print(f"  EDDI {feature} {year}-{month:02d}: {len(days)} daily grids", flush=True)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one_day, d): d for d in days}
        done = 0
        for fut in as_completed(futs):
            day, samples = fut.result()
            valid = ~np.isnan(samples)
            sums[valid] += samples[valid]
            counts[valid] += 1
            done += 1
            if done % 10 == 0 or done == len(days):
                print(f"    {feature} {year}-{month:02d}: {done}/{len(days)} days", flush=True)

    with np.errstate(divide="ignore", invalid="ignore"):
        means = np.where(counts > 0, sums / counts, np.nan)

    out = {code: (None if math.isnan(val) else float(val)) for code, val in zip(codes, means)}
    with cache_path.open("w") as f:
        json.dump(out, f)
    return out


def write_output(path: Path, rows: List[dict]) -> None:
    fieldnames = ["COUNTY_MUNI_CODE", "Latitude", "Longitude", "year", "month"] + FEATURES
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            out = {}
            for k in fieldnames:
                v = row.get(k)
                if isinstance(v, float):
                    out[k] = "" if math.isnan(v) else f"{v:.8g}"
                elif v is None:
                    out[k] = ""
                else:
                    out[k] = v
            writer.writerow(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--counties",
        type=Path,
        default=Path.home() / "Downloads" / "county_list.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path.home() / "Downloads" / "county_weather_monthly_2026_04_06.csv",
    )
    parser.add_argument("--start", default="2026-04-01")
    parser.add_argument("--end", default="2026-06-30")
    parser.add_argument("--batch-size", type=int, default=40)
    parser.add_argument("--cache-dir", type=Path, default=Path("/tmp/weather_cache"))
    parser.add_argument("--eddi-workers", type=int, default=6)
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d").date()
    end = datetime.strptime(args.end, "%Y-%m-%d").date()
    args.cache_dir.mkdir(parents=True, exist_ok=True)

    counties = load_counties(args.counties)
    print(f"Loaded {len(counties)} counties from {args.counties}", flush=True)

    # Also copy repo output
    repo_output = Path("/workspace/data") / args.output.name

    all_rows: List[dict] = []
    for year, month, ms, me in month_windows(start, end):
        print(f"\n=== {year}-{month:02d} ({ms} to {me}) ===", flush=True)
        weather = fetch_weather_for_month(
            counties, year, month, ms, me, args.batch_size, args.cache_dir
        )
        eddi_03 = fetch_eddi_month(
            counties, "EDDI_ETrs_03m", year, month, ms, me, args.cache_dir, args.eddi_workers
        )
        eddi_06 = fetch_eddi_month(
            counties, "EDDI_ETrs_06wk", year, month, ms, me, args.cache_dir, args.eddi_workers
        )

        for c in counties:
            code = c["COUNTY_MUNI_CODE"]
            row = {
                "COUNTY_MUNI_CODE": code,
                "Latitude": c["Latitude"],
                "Longitude": c["Longitude"],
                "year": year,
                "month": month,
            }
            w = weather.get(code, {})
            for feat in FEATURES:
                if feat == "EDDI_ETrs_03m":
                    val = eddi_03.get(code)
                    row[feat] = float("nan") if val is None else float(val)
                elif feat == "EDDI_ETrs_06wk":
                    val = eddi_06.get(code)
                    row[feat] = float("nan") if val is None else float(val)
                else:
                    val = w.get(feat, float("nan"))
                    row[feat] = float(val) if val is not None else float("nan")
            all_rows.append(row)

        # checkpoint write after each month
        write_output(args.output, all_rows)
        write_output(repo_output, all_rows)
        print(f"Wrote checkpoint ({len(all_rows)} rows) -> {args.output}", flush=True)

    print(f"\nDone. {len(all_rows)} rows written to {args.output} and {repo_output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
