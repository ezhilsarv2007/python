# B3 - daily mean PM2.5 per station: plain loops vs pandas groupby vs SQL GROUP BY
import cProfile
import csv
import io
import os
import pstats
import sqlite3
import statistics
import time
from collections import defaultdict

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))


def make_csv(n_stations, path, days=365):
    """Hourly readings for a year: 24*365 = 8,760 rows per station."""
    rng = np.random.default_rng(42)
    per = days * 24
    hours = np.arange(per)
    day_str = (pd.Timestamp("2025-01-01") + pd.to_timedelta(hours // 24, unit="D")).strftime("%Y-%m-%d")
    frames = []
    for s in range(n_stations):
        base = 40 + (s * 7) % 80
        pm = np.round(np.clip(rng.normal(base, 15, per), 3, None), 1)
        frames.append(pd.DataFrame({"station": f"Station{s:03d}", "date": day_str,
                                    "hour": hours % 24, "pm25": pm}))
    pd.concat(frames).to_csv(path, index=False)


# ---------------- method 1: plain python ----------------
def by_loops(path):
    groups = defaultdict(list)
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            groups[(row["station"], row["date"])].append(float(row["pm25"]))
    return {key: statistics.mean(vals) for key, vals in groups.items()}


# ---------------- method 2: pandas ----------------
def by_pandas(path):
    df = pd.read_csv(path)
    out = df.groupby(["station", "date"])["pm25"].mean()
    return out.to_dict()


# ---------------- method 3: SQL ----------------
def sql_load(path):
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE r (station TEXT, day TEXT, hour INTEGER, pm25 REAL)")
    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader)                                         # skip header
        con.executemany("INSERT INTO r VALUES (?,?,?,?)",
                        ((a, b, int(c), float(d)) for a, b, c, d in reader))
    con.commit()
    return con


def sql_query(con):
    rows = con.execute("SELECT station, day, AVG(pm25) FROM r GROUP BY station, day").fetchall()
    return {(s, d): v for s, d, v in rows}


# ---------------- alternative: one pass with running sum and count ----------------
def by_running_sum(path):
    total, count = {}, {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            key = (row["station"], row["date"])
            total[key] = total.get(key, 0.0) + float(row["pm25"])
            count[key] = count.get(key, 0) + 1
    return {k: total[k] / count[k] for k in total}


def same(a, b):
    return a.keys() == b.keys() and all(abs(a[k] - b[k]) < 1e-9 for k in a)


def timed(fn, *args):
    t = time.perf_counter()
    result = fn(*args)
    return result, time.perf_counter() - t


if __name__ == "__main__":
    print("=" * 72)
    print("B3.1 correctness on a small file (1 station, 3 days of hourly data)")
    print("=" * 72)
    small = os.path.join(HERE, "small.csv")
    rng = np.random.default_rng(1)
    rows = ["station,date,hour,pm25"]
    for d in range(1, 4):
        for h in range(24):
            rows.append(f"Adyar,2025-01-0{d},{h},{round(float(rng.uniform(20, 90)), 1)}")
    open(small, "w").write("\n".join(rows) + "\n")
    a, b = by_loops(small), by_pandas(small)
    con = sql_load(small); c = sql_query(con)
    d_ = by_running_sum(small)
    print(f"{'station':<8}{'date':<12}{'loops':>9}{'pandas':>9}{'sql':>9}{'running':>9}")
    for key in sorted(a):
        print(f"{key[0]:<8}{key[1]:<12}{a[key]:>9.3f}{b[key]:>9.3f}{c[key]:>9.3f}{d_[key]:>9.3f}")
    print("loops == pandas == sql == running sum:", same(a, b) and same(a, c) and same(a, d_))
    os.remove(small)

    print("\n" + "=" * 72)
    print("B3.2 time for 1, 12 and 120 stations (a year of hourly data each)")
    print("=" * 72)
    print(f"{'stations':>8} {'rows':>10} | {'loops':>8} {'pandas':>8} {'SQL load':>9} {'SQL query':>10} {'SQL total':>10} {'running':>8}")
    sizes = {}
    for n in (1, 12, 120):
        path = os.path.join(HERE, f"data_{n}.csv")
        make_csv(n, path)
        sizes[n] = path
        r1, t1 = timed(by_loops, path)
        r2, t2 = timed(by_pandas, path)
        con, t3 = timed(sql_load, path)
        r3, t4 = timed(sql_query, con)
        r4, t5 = timed(by_running_sum, path)
        assert same(r1, r2) and same(r1, r3) and same(r1, r4)
        rows_n = n * 8760
        print(f"{n:>8} {rows_n:>10} | {t1:>7.3f}s {t2:>7.3f}s {t3:>8.3f}s {t4:>9.3f}s {t3 + t4:>9.3f}s {t5:>7.3f}s")
        con.close()
    print("(all methods gave identical answers at every size)")

    print("\n" + "=" * 72)
    print("B3.3 cProfile of the plain-Python version (12 stations)")
    print("=" * 72)
    prof = cProfile.Profile()
    prof.runcall(by_loops, sizes[12])
    buf = io.StringIO()
    pstats.Stats(prof, stream=buf).sort_stats("tottime").print_stats(8)
    lines = [l for l in buf.getvalue().splitlines() if l.strip()]
    print("\n".join(lines))

    for p in sizes.values():
        os.remove(p)
