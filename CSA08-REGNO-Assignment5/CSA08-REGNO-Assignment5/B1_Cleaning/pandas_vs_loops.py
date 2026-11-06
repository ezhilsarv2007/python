# B1 alternative concept: same cleaning rules with pandas instead of csv + loops
import csv
import os
import time
import tracemalloc

import numpy as np
import pandas as pd

from cleaning_pipeline import clean_rows, FAHRENHEIT_STATIONS, LIMITS, VALUE_COLUMNS

HERE = os.path.dirname(os.path.abspath(__file__))
STATIONS = [f"Station{i:02d}" for i in range(12)]
F_STATIONS = {"Station00", "Station01"}


def make_file(n, path):
    """n rows in time order, 12 stations, with missing and impossible values."""
    rng = np.random.default_rng(5)
    idx = np.arange(n)
    day = idx // (12 * 24)
    df = pd.DataFrame({
        "station": np.array(STATIONS)[idx % 12],
        "date": (pd.Timestamp("2020-01-01") + pd.to_timedelta(day, unit="D")).strftime("%Y-%m-%d"),
        "hour": (idx // 12) % 24,
        "pm25": np.round(rng.normal(80, 25, n).clip(5), 1).astype(object),
        "pm10": np.round(rng.normal(140, 40, n).clip(5), 1),
        "no2": np.round(rng.normal(40, 10, n).clip(1), 1),
        "temp": np.round(rng.normal(28, 4, n), 1),
    })
    r = rng.random(n)
    df.loc[r < 0.03, "pm25"] = "NA"
    df.loc[(r >= 0.03) & (r < 0.04), "pm25"] = -9
    df.loc[(r >= 0.04) & (r < 0.045), "pm25"] = 9999
    df.to_csv(path, index=False)


def clean_with_loops(path):
    with open(path, newline="") as f:
        cleaned, _ = clean_rows(csv.DictReader(f))
    return cleaned


def clean_with_pandas(path):
    df = pd.read_csv(path)
    df["station"] = df["station"].str.strip().str.title()
    for col in VALUE_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")           # NA / text -> NaN
    f_mask = df["station"].str.lower().isin(FAHRENHEIT_STATIONS)
    df.loc[f_mask, "temp"] = (df.loc[f_mask, "temp"] - 32) * 5 / 9
    for col in VALUE_COLUMNS:
        lo, hi = LIMITS[col]
        df.loc[(df[col] < lo) | (df[col] > hi), col] = np.nan       # impossible -> missing
    df = df.drop_duplicates(subset=["station", "date", "hour"])
    df[VALUE_COLUMNS] = df.groupby("station")[VALUE_COLUMNS].ffill()  # previous value
    df = df.dropna(subset=["pm25"])
    return df


def current_rss_mb():
    with open("/proc/self/status") as f:
        for line in f:
            if line.startswith("VmRSS"):
                return int(line.split()[1]) / 1024


def worker(which, path):
    """Runs in its own process so the time and memory of one method are not mixed up
    with the other. tracemalloc is NOT used because it slows plain Python loops a lot."""
    import resource
    FAHRENHEIT_STATIONS.clear()
    FAHRENHEIT_STATIONS.update(s.lower() for s in F_STATIONS)
    before = current_rss_mb()
    t = time.perf_counter()
    result = clean_with_loops(path) if which == "loops" else clean_with_pandas(path)
    elapsed = time.perf_counter() - t
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    if which == "loops":
        rows, total = len(result), sum(r["pm25"] for r in result)
    else:
        rows, total = len(result), float(result["pm25"].sum())
    print(f"{elapsed:.4f} {max(peak - before, 0):.1f} {rows} {total:.2f}")


def run_worker(which, path):
    import subprocess, sys
    out = subprocess.run([sys.executable, __file__, "worker", which, path],
                         capture_output=True, text=True, check=True).stdout.split()
    return float(out[0]), float(out[1]), int(out[2]), float(out[3])


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "worker":
        worker(sys.argv[2], sys.argv[3])
        sys.exit()

    print("Same cleaning rules, two implementations (each run in its own process)")
    print(f"{'rows':>10} | {'loop time':>10} {'loop MB':>8} | {'pandas time':>11} {'pandas MB':>10} | speed-up | same rows | same pm25 sum")
    for n in (1_000, 100_000, 1_000_000):
        path = os.path.join(HERE, f"tmp_{n}.csv")
        make_file(n, path)
        ta, ma, ra, sa = run_worker("loops", path)
        tb, mb, rb, sb = run_worker("pandas", path)
        print(f"{n:>10} | {ta:>9.3f}s {ma:>8.1f} | {tb:>10.3f}s {mb:>10.1f} | {ta / tb:>7.1f}x | {ra == rb!s:>9} | {abs(sa - sb) < 1.0}")
        os.remove(path)
    print("\n(memory = peak extra MB of the process while cleaning, measured with resource.getrusage)")
