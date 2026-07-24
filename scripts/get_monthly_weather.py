#!/usr/bin/env python3
"""
Get monthly weather averages for counties in county_list.csv

WHAT THIS DOES
  Reads your county list (code + lat/lon), downloads weather from Open-Meteo,
  and saves monthly averages to a CSV file.

SETUP (one time)
  1. Put county_list.csv in your Downloads folder
  2. Open a terminal in this folder
  3. Run:  pip install numpy

EACH MONTH (after the month has ended)
  python get_monthly_weather.py --month 2026-07

  Or automatically use last month:
  python get_monthly_weather.py --latest

FIRST TIME / SEVERAL MONTHS
  python get_monthly_weather.py --start 2026-04-01 --end 2026-06-30

Output file (created/updated automatically):
  ~/Downloads/county_weather_monthly.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np

# Columns written to the output CSV (after id fields).
FEATURES = [
    "t2m",
    "t850",
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
    "tp",
]

HOURLY_VARS = [
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

API_URL = "https://historical-forecast-api.open-meteo.com/v1/forecast"


def previous_month(today=None):
    today = today or date.today()
    end = date(today.year, today.month, 1) - timedelta(days=1)
    start = date(end.year, end.month, 1)
    return start, end


def month_range(year, month):
    start = date(year, month, 1)
    if month == 12:
        end = date(year, 12, 31)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)
    return start, end


def iter_months(start, end):
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        ms, me = month_range(y, m)
        yield y, m, max(ms, start), min(me, end)
        if m == 12:
            y, m = y + 1, 1
        else:
            m += 1


def specific_humidity(temp_c, rh_pct, pressure_hpa):
    """kg/kg from temperature (C), relative humidity (%), pressure (hPa)."""
    es = 6.112 * np.exp((17.67 * temp_c) / (temp_c + 243.5))
    e = (rh_pct / 100.0) * es
    return 0.622 * e / (pressure_hpa - 0.378 * e)


def mean_ok(arr):
    arr = np.asarray(arr, dtype=float)
    if arr.size == 0 or np.all(np.isnan(arr)):
        return float("nan")
    return float(np.nanmean(arr))


def daily_totals(times, values):
    buckets = defaultdict(list)
    for t, v in zip(times, values):
        if v is None:
            continue
        buckets[t[:10]].append(float(v))
    return {d: float(np.sum(vals)) for d, vals in buckets.items()}


def is_rate_limit(err):
    text = str(err)
    return "429" in text or "Too Many Requests" in text


def http_json(url, retries=10):
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "get-monthly-weather/1.0"})
            with urllib.request.urlopen(req, timeout=300) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as err:
            last_err = err
            if is_rate_limit(err):
                # Open-Meteo asks us to slow down; wait longer each time.
                wait = min(30 * (2 ** attempt), 300)
                print(f"  Too many requests — pausing {wait}s, then retrying…")
            else:
                wait = min(2 ** attempt, 60)
                print(f"  Network issue, retrying in {wait}s… ({err})")
            time.sleep(wait)
    raise RuntimeError(f"Could not download data:\n{url}") from last_err


def load_counties(path):
    path = Path(path)
    if not path.exists():
        sys.exit(
            f"Could not find county file:\n  {path}\n"
            "Put county_list.csv in your Downloads folder, or pass --counties PATH"
        )
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    needed = {"COUNTY_MUNI_CODE", "Latitude", "Longitude"}
    if not rows or not needed.issubset(rows[0].keys()):
        sys.exit(f"{path} must have columns: COUNTY_MUNI_CODE, Latitude, Longitude")
    for r in rows:
        r["Latitude"] = float(r["Latitude"])
        r["Longitude"] = float(r["Longitude"])
    return rows


def fetch_batch(lats, lons, start, end):
    params = {
        "latitude": ",".join(f"{x:.6f}" for x in lats),
        "longitude": ",".join(f"{x:.6f}" for x in lons),
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "hourly": ",".join(HOURLY_VARS),
        "daily": "temperature_2m_max",
        "models": "ecmwf_ifs025",
        "wind_speed_unit": "ms",
        "timezone": "GMT",
    }
    url = API_URL + "?" + urllib.parse.urlencode(params)
    data = http_json(url)
    if isinstance(data, dict):
        if data.get("error"):
            raise RuntimeError(data.get("reason", "API error"))
        return [data]
    return data


def averages_for_one_place(payload):
    h = payload["hourly"]
    d = payload["daily"]
    times = h["time"]

    t850 = np.array(h["temperature_850hPa"], dtype=float)
    t250 = np.array(h["temperature_250hPa"], dtype=float)
    r850 = np.array(h["relative_humidity_850hPa"], dtype=float)
    r250 = np.array(h["relative_humidity_250hPa"], dtype=float)

    precip = daily_totals(times, h["precipitation"])
    runoff = daily_totals(times, h["runoff"])
    tmax_vals = [v for v in d["temperature_2m_max"] if v is not None]

    return {
        "t2m": mean_ok(h["temperature_2m"]),
        "t850": mean_ok(t850),
        "t250": mean_ok(t250),
        "q250": mean_ok(specific_humidity(t250, r250, 250.0)),
        "q850": mean_ok(specific_humidity(t850, r850, 850.0)),
        "tmax": float(np.mean(tmax_vals)) if tmax_vals else float("nan"),
        "r500": mean_ok(h["relative_humidity_500hPa"]),
        "r850": mean_ok(r850),
        "r250": mean_ok(r250),
        "u850": mean_ok(h["wind_u_component_850hPa"]),
        "u250": mean_ok(h["wind_u_component_250hPa"]),
        "v500": mean_ok(h["wind_v_component_500hPa"]),
        "v250": mean_ok(h["wind_v_component_250hPa"]),
        "v850": mean_ok(h["wind_v_component_850hPa"]),
        "u10": mean_ok(h["wind_u_component_10m"]),
        "v10": mean_ok(h["wind_v_component_10m"]),
        "d2m": mean_ok(h["dew_point_2m"]),
        "sp": mean_ok(h["surface_pressure"]),
        "SRO": float(np.mean(list(runoff.values()))) if runoff else float("nan"),
        "tp": float(np.mean(list(precip.values()))) if precip else float("nan"),
    }


def fmt(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return ""
    if isinstance(v, float):
        return f"{v:.8g}"
    return str(v)


def load_existing(path):
    path = Path(path)
    if not path.exists():
        return []
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["year"] = int(r["year"])
        r["month"] = int(r["month"])
        r["Latitude"] = float(r["Latitude"])
        r["Longitude"] = float(r["Longitude"])
        for feat in FEATURES:
            if feat in r and r[feat] != "":
                r[feat] = float(r[feat])
            elif feat in r:
                r[feat] = float("nan")
    return rows


def save_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["COUNTY_MUNI_CODE", "Latitude", "Longitude", "year", "month"] + FEATURES
    rows = sorted(rows, key=lambda r: (r["year"], r["month"], r["COUNTY_MUNI_CODE"]))
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: fmt(r.get(k, "")) for k in fields})


def merge(old_rows, new_rows):
    """Keep old data, replace any county+year+month that we just downloaded."""
    index = {(r["COUNTY_MUNI_CODE"], r["year"], r["month"]): r for r in old_rows}
    for r in new_rows:
        index[(r["COUNTY_MUNI_CODE"], r["year"], r["month"])] = r
    return list(index.values())


def process_month(counties, year, month, start, end, batch_size, pause_seconds):
    print(f"\nDownloading {year}-{month:02d} ({start} to {end}) …")
    weather = {}
    n = len(counties)
    for i in range(0, n, batch_size):
        batch = counties[i : i + batch_size]
        print(f"  Counties {i + 1}-{i + len(batch)} of {n}")
        payloads = fetch_batch(
            [c["Latitude"] for c in batch],
            [c["Longitude"] for c in batch],
            start,
            end,
        )
        for county, payload in zip(batch, payloads):
            weather[county["COUNTY_MUNI_CODE"]] = averages_for_one_place(payload)
        # Pause between requests so the free weather API does not block us.
        if i + batch_size < n:
            print(f"  Pausing {pause_seconds}s before next request…")
            time.sleep(pause_seconds)

    rows = []
    for c in counties:
        code = c["COUNTY_MUNI_CODE"]
        row = {
            "COUNTY_MUNI_CODE": code,
            "Latitude": c["Latitude"],
            "Longitude": c["Longitude"],
            "year": year,
            "month": month,
        }
        row.update(weather[code])
        rows.append(row)
    return rows


def main():
    p = argparse.ArgumentParser(
        description="Download monthly weather averages for your county list.",
    )
    p.add_argument(
        "--counties",
        default=str(Path.home() / "Downloads" / "county_list.csv"),
        help="Path to county_list.csv (default: ~/Downloads/county_list.csv)",
    )
    p.add_argument(
        "--output",
        default=str(Path.home() / "Downloads" / "county_weather_monthly.csv"),
        help="Where to save results (default: ~/Downloads/county_weather_monthly.csv)",
    )
    p.add_argument("--latest", action="store_true", help="Use the previous calendar month")
    p.add_argument("--month", help="One month like 2026-06")
    p.add_argument("--start", help="Start date YYYY-MM-DD (with --end)")
    p.add_argument("--end", help="End date YYYY-MM-DD (with --start)")
    p.add_argument(
        "--batch-size",
        type=int,
        default=20,
        help="How many counties per download (smaller = gentler on the API)",
    )
    p.add_argument(
        "--pause",
        type=float,
        default=5.0,
        help="Seconds to wait between API requests (default: 5)",
    )
    args = p.parse_args()

    chosen = sum([bool(args.latest), bool(args.month), bool(args.start or args.end)])
    if chosen != 1:
        p.error("Please choose ONE of: --latest   OR   --month 2026-06   OR   --start/--end")

    if args.latest:
        start, end = previous_month()
    elif args.month:
        dt = datetime.strptime(args.month, "%Y-%m")
        start, end = month_range(dt.year, dt.month)
    else:
        if not args.start or not args.end:
            p.error("For a date range, provide both --start and --end")
        start = datetime.strptime(args.start, "%Y-%m-%d").date()
        end = datetime.strptime(args.end, "%Y-%m-%d").date()

    counties = load_counties(args.counties)
    print(f"Found {len(counties)} counties in {args.counties}")
    print(f"Saving to {args.output}")
    print(f"Period: {start} through {end}")
    print("(This can take a while for thousands of counties.)")

    existing = load_existing(args.output)
    all_new = []
    for year, month, ms, me in iter_months(start, end):
        month_rows = process_month(
            counties, year, month, ms, me, args.batch_size, args.pause
        )
        all_new.extend(month_rows)
        combined = merge(existing, all_new)
        save_csv(args.output, combined)
        print(f"  Saved progress: {len(combined)} rows in {args.output}")

    print("\nFinished.")
    print(f"Open this file: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
