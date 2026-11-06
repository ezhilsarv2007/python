# B1 - cleaning pipeline for the city air-quality network
# acquire -> inspect -> clean -> normalise -> store -> query -> visualise
import csv
import io
import os
import random
import sqlite3
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")                  # no window, just save the pictures
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------- settings (all rules in one place) ----------------
FAHRENHEIT_STATIONS = {"guindy", "velachery"}     # these two send temperature in F
LIMITS = {"pm25": (0, 999), "pm10": (0, 999), "no2": (0, 999), "temp": (-10, 55)}
MISSING_WORDS = {"", "na", "n/a", "nan", "null"}
VALUE_COLUMNS = ["pm25", "pm10", "no2", "temp"]


# ---------------- small helper functions ----------------
def to_number(text):
    """Text -> float, or None if it is blank / NA / not a number."""
    if text is None:
        return None
    t = text.strip()
    if t.lower() in MISSING_WORDS:
        return None
    try:
        return float(t)
    except ValueError:
        return None


def clean_station(name):
    return " ".join(name.strip().split()).title()       # " adyar " -> "Adyar"


def clean_date(text):
    """Accepts 2026-10-01 or 01/10/2026 and always returns 2026-10-01 (or None)."""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(text.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


def f_to_c(f):
    return (f - 32) * 5 / 9


def clean_rows(rows):
    """rows: iterable of dicts straight from csv.DictReader, in time order.
    Returns (clean_list, stats). clean_list holds dicts with standard formats."""
    stats = {"read": 0, "bad_date": 0, "duplicates": 0, "fahrenheit_converted": 0,
             "impossible_to_missing": 0, "forward_filled": 0, "dropped_no_previous": 0}
    seen = set()
    last_good = {}                   # station -> {column: last valid value}
    out = []

    for raw in rows:
        stats["read"] += 1
        station = clean_station(raw["station"])
        day = clean_date(raw["date"])
        if day is None:
            stats["bad_date"] += 1
            continue
        hour = int(float(raw["hour"]))
        key = (station, day, hour)
        if key in seen:                              # same station/date/hour twice
            stats["duplicates"] += 1
            continue
        seen.add(key)

        values = {}
        for col in VALUE_COLUMNS:
            v = to_number(raw.get(col))
            if v is not None and col == "temp" and station.lower() in FAHRENHEIT_STATIONS:
                v = f_to_c(v)
                stats["fahrenheit_converted"] += 1
            if v is not None:
                lo, hi = LIMITS[col]
                if v < lo or v > hi:                 # impossible -> treat as missing
                    v = None
                    stats["impossible_to_missing"] += 1
            values[col] = v

        memory = last_good.setdefault(station, {})
        for col in VALUE_COLUMNS:
            if values[col] is None and col in memory:
                values[col] = memory[col]            # forward fill: previous value
                stats["forward_filled"] += 1
            elif values[col] is not None:
                memory[col] = values[col]

        if values["pm25"] is None:                   # nothing to fill from, drop the row
            stats["dropped_no_previous"] += 1
            continue

        out.append({"station": station, "day": day, "hour": hour,
                    "pm25": round(values["pm25"], 1),
                    "pm10": None if values["pm10"] is None else round(values["pm10"], 1),
                    "no2": None if values["no2"] is None else round(values["no2"], 1),
                    "temp": None if values["temp"] is None else round(values["temp"], 1)})
    return out, stats


def min_max(values):
    lo, hi = min(values), max(values)
    return [0.0 if hi == lo else round((v - lo) / (hi - lo), 3) for v in values]


def z_score(values):
    n = len(values)
    mean = sum(values) / n
    sd = (sum((v - mean) ** 2 for v in values) / n) ** 0.5
    return [0.0 if sd == 0 else round((v - mean) / sd, 3) for v in values]


# ---------------- Part 1: small file with EVERY problem ----------------
SMALL = """station,date,hour,pm25,pm10,no2,temp
Adyar,2026-10-01,8,48,90,30,29.5
Adyar,2026-10-01,9,NA,92,31,30.1
Adyar,2026-10-01,10,,95,,30.8
Adyar,2026-10-01,10,,95,,30.8
 adyar ,2026-10-01,11,-5,88,29,31.0
Adyar,01/10/2026,12,55,100,35,31.2
Adyar,2026-10-01,13,5000,99,36,31.9
Guindy,2026-10-01,8,95,160,40,86.0
Guindy,2026-10-01,9,101,170,42,88.5
Guindy,2026-10-01,10,abc,175,44,90.0
Manali,not-a-date,8,70,120,33,30.0
Manali,2026-10-01,8,NA,120,33,30.0
Manali,2026-10-01,9,130,200,50,31.0
"""


def show_table(rows, title):
    print(title)
    print(f"  {'station':<9}{'date':<12}{'hour':>4}{'pm25':>8}{'pm10':>7}{'no2':>6}{'temp':>7}")
    for r in rows:
        print(f"  {str(r['station']):<9}{str(r['date']):<12}{str(r['hour']):>4}"
              f"{str(r['pm25']):>8}{str(r['pm10']):>7}{str(r['no2']):>6}{str(r['temp']):>7}")


def part1():
    print("=" * 70)
    print("PART 1 - small file containing every problem from A1.1")
    print("=" * 70)
    raw_rows = list(csv.DictReader(io.StringIO(SMALL)))
    show_table([{"station": r["station"], "date": r["date"], "hour": r["hour"], "pm25": r["pm25"],
                 "pm10": r["pm10"], "no2": r["no2"], "temp": r["temp"]} for r in raw_rows],
               "\nBEFORE cleaning (13 rows):")
    cleaned, stats = clean_rows(raw_rows)
    cleaned_show = [dict(r, date=r["day"]) for r in cleaned]
    show_table(cleaned_show, f"\nAFTER cleaning ({len(cleaned)} rows):")
    print("\nWhat the cleaner did:")
    for k, v in stats.items():
        print(f"  {k:<24}{v}")
    print("\nNotes:")
    print("  - Guindy temperature 86.0 F became 30.0 C (Guindy is a Fahrenheit station)")
    print("  - the 5000 and -5 pm25 values were treated as missing and then forward filled")
    print("  - the 'abc' pm25 for Guindy was filled with the previous value 101")
    print("  - Manali's first row had a bad date and was dropped; its next row had NA pm25 and")
    print("    no previous value to copy, so it was dropped too")

    vals = [r["pm25"] for r in cleaned]
    print("\nNormalisation of the cleaned pm25 values:", vals)
    print("  min-max :", min_max(vals))
    print("  z-score :", z_score(vals))


# ---------------- Part 2: bigger messy data -> clean -> SQLite -> SQL -> charts ----------------
def make_month_data(path):
    """One month (Oct 2026), 4 stations, hourly, with faults injected. Written as CSV."""
    random.seed(2026)
    base = {"Adyar": 45, "Guindy": 85, "Velachery": 60, "Manali": 110}
    start = datetime(2026, 10, 1)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["station", "date", "hour", "pm25", "pm10", "no2", "temp"])
        for d in range(31):
            day = start + timedelta(days=d)
            for h in range(24):
                for st, b in base.items():
                    temp_c = 27 + 5 * (1 if 11 <= h <= 16 else 0) - 3 * (1 if h < 6 else 0) + random.uniform(-1, 1)
                    rush = 25 if h in (7, 8, 9, 19, 20, 21) else 0
                    pm25 = max(5, b + rush + (30 - temp_c) * 2 + random.gauss(0, 8))
                    pm10 = pm25 * 1.8 + random.gauss(0, 5)
                    no2 = pm25 * 0.5 + random.gauss(0, 3)
                    temp = temp_c * 9 / 5 + 32 if st.lower() in FAHRENHEIT_STATIONS else temp_c
                    row = [st, day.strftime("%Y-%m-%d"), h,
                           round(pm25, 1), round(pm10, 1), round(no2, 1), round(temp, 1)]
                    r = random.random()
                    if r < 0.03:
                        row[3] = random.choice(["", "NA"])           # missing
                    elif r < 0.04:
                        row[3] = random.choice([-9, -1, 4500, 9999])  # sensor fault
                    w.writerow(row)
                    if random.random() < 0.002:
                        w.writerow(row)                              # duplicate row


def part2():
    print("\n" + "=" * 70)
    print("PART 2 - one month of data: clean, store in SQLite, query, chart")
    print("=" * 70)
    csv_path = os.path.join(HERE, "october_stations.csv")
    make_month_data(csv_path)
    with open(csv_path, newline="") as f:
        cleaned, stats = clean_rows(csv.DictReader(f))
    print("rows cleaned:", len(cleaned))
    for k, v in stats.items():
        print(f"  {k:<24}{v}")

    # ---- SQLite storage ----
    db_path = os.path.join(HERE, "airquality.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    con = sqlite3.connect(db_path)
    con.executescript("""
        CREATE TABLE stations (station_id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL);
        CREATE TABLE readings (
            station_id INTEGER NOT NULL REFERENCES stations(station_id),
            day   TEXT    NOT NULL,
            hour  INTEGER NOT NULL,
            pm25  REAL    NOT NULL,
            pm10  REAL,
            no2   REAL,
            temp_c REAL,
            PRIMARY KEY (station_id, day, hour));
    """)
    names = sorted({r["station"] for r in cleaned})
    con.executemany("INSERT INTO stations (name) VALUES (?)", [(n,) for n in names])
    ids = dict(con.execute("SELECT name, station_id FROM stations"))
    con.executemany("INSERT INTO readings VALUES (?,?,?,?,?,?,?)",
                    [(ids[r["station"]], r["day"], r["hour"], r["pm25"], r["pm10"], r["no2"], r["temp"])
                     for r in cleaned])
    con.commit()
    print("rows stored in SQLite:", con.execute("SELECT COUNT(*) FROM readings").fetchone()[0])

    # ---- the three questions from A1.3 ----
    print("\nQ1. Average PM2.5 of Adyar in October 2026:")
    q1 = con.execute("""SELECT ROUND(AVG(r.pm25),2) FROM readings r JOIN stations s USING (station_id)
                        WHERE s.name = ? AND r.day BETWEEN '2026-10-01' AND '2026-10-31'""", ("Adyar",)).fetchone()[0]
    print("   ", q1)

    print("\nQ2. Stations ranked by average PM2.5 (worst first):")
    q2 = con.execute("""SELECT s.name, ROUND(AVG(r.pm25),2) FROM readings r JOIN stations s USING (station_id)
                        GROUP BY s.name ORDER BY 2 DESC""").fetchall()
    for name, avg in q2:
        print(f"    {name:<10}{avg}")

    print("\nQ3. The three hours of the day with the worst average PM2.5:")
    q3 = con.execute("SELECT hour, ROUND(AVG(pm25),2) FROM readings GROUP BY hour ORDER BY 2 DESC LIMIT 3").fetchall()
    for h, avg in q3:
        print(f"    {h:02d}:00   {avg}")

    # ---- charts ----
    daily = con.execute("""SELECT s.name, r.day, AVG(r.pm25) FROM readings r JOIN stations s USING (station_id)
                           GROUP BY s.name, r.day ORDER BY r.day""").fetchall()
    charts = []

    # 1. line chart - trend
    plt.figure(figsize=(9, 4.5))
    for st in names:
        pts = [(d, v) for n, d, v in daily if n == st]
        plt.plot([int(d[-2:]) for d, _ in pts], [v for _, v in pts], label=st)
    plt.xlabel("Day of October 2026"); plt.ylabel("Daily mean PM2.5 (ug/m3)")
    plt.title("PM2.5 trend over October 2026"); plt.legend(); plt.grid(alpha=0.3)
    plt.tight_layout(); plt.savefig(os.path.join(HERE, "chart1_trend_line.png"), dpi=120); plt.close()
    charts.append(("chart1_trend_line.png", "line chart of the daily mean PM2.5 for each station"))

    # 2. bar chart + box plot - compare stations
    plt.figure(figsize=(6.5, 4.5))
    plt.bar([n for n, _ in q2], [a for _, a in q2], color="steelblue")
    plt.xlabel("Station"); plt.ylabel("Mean PM2.5 (ug/m3)"); plt.title("Mean PM2.5 by station")
    plt.tight_layout(); plt.savefig(os.path.join(HERE, "chart2_station_bar.png"), dpi=120); plt.close()
    charts.append(("chart2_station_bar.png", "bar chart comparing stations"))

    box_data = [[r[0] for r in con.execute(
        "SELECT pm25 FROM readings WHERE station_id = ?", (ids[st],))] for st in names]
    plt.figure(figsize=(6.5, 4.5))
    plt.boxplot(box_data, tick_labels=names)
    plt.xlabel("Station"); plt.ylabel("PM2.5 (ug/m3)"); plt.title("Spread of PM2.5 readings by station")
    plt.tight_layout(); plt.savefig(os.path.join(HERE, "chart3_station_box.png"), dpi=120); plt.close()
    charts.append(("chart3_station_box.png", "box plot showing spread and outliers per station"))

    # 3. scatter - temperature vs pm25
    pts = con.execute("SELECT temp_c, pm25 FROM readings WHERE temp_c IS NOT NULL").fetchall()
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    plt.figure(figsize=(6.5, 4.5))
    plt.scatter(xs, ys, s=4, alpha=0.3)
    plt.xlabel("Temperature (C)"); plt.ylabel("PM2.5 (ug/m3)"); plt.title("Temperature vs PM2.5")
    plt.tight_layout(); plt.savefig(os.path.join(HERE, "chart4_temp_scatter.png"), dpi=120); plt.close()
    charts.append(("chart4_temp_scatter.png", "scatter plot of temperature against PM2.5"))
    n = len(xs); mx, my = sum(xs) / n, sum(ys) / n
    corr = (sum((x - mx) * (y - my) for x, y in zip(xs, ys)) /
            ((sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5))

    # 4. hour of day - bar (and histogram of values)
    by_hour = con.execute("SELECT hour, AVG(pm25) FROM readings GROUP BY hour ORDER BY hour").fetchall()
    plt.figure(figsize=(8, 4.5))
    plt.bar([h for h, _ in by_hour], [a for _, a in by_hour], color="indianred")
    plt.xlabel("Hour of day"); plt.ylabel("Mean PM2.5 (ug/m3)"); plt.title("Average PM2.5 by hour of day")
    plt.tight_layout(); plt.savefig(os.path.join(HERE, "chart5_hour_bar.png"), dpi=120); plt.close()
    charts.append(("chart5_hour_bar.png", "bar chart of the average PM2.5 for each hour"))

    plt.figure(figsize=(6.5, 4.5))
    plt.hist([r[0] for r in con.execute("SELECT pm25 FROM readings")], bins=30, color="seagreen")
    plt.xlabel("PM2.5 (ug/m3)"); plt.ylabel("Number of readings"); plt.title("Distribution of PM2.5 readings")
    plt.tight_layout(); plt.savefig(os.path.join(HERE, "chart6_histogram.png"), dpi=120); plt.close()
    charts.append(("chart6_histogram.png", "histogram of all PM2.5 readings"))

    print("\nCharts saved:")
    for f, d in charts:
        print(f"  {f:<26} {d}")

    # ---- interpretation (numbers come from the data above) ----
    worst, best = q2[0], q2[-1]
    peak_hour = max(by_hour, key=lambda p: p[1])
    low_hour = min(by_hour, key=lambda p: p[1])
    first = [v for n, d, v in daily if n == worst[0]][:7]
    last = [v for n, d, v in daily if n == worst[0]][-7:]
    print("\nInterpretation:")
    print(f"  Line chart  : all four lines stay roughly flat through the month, with day-to-day wiggles.")
    print(f"                {worst[0]} is always the highest line and {best[0]} the lowest. The first week of")
    print(f"                {worst[0]} averages {sum(first)/len(first):.1f} and the last week {sum(last)/len(last):.1f}, so there is no clear trend.")
    print(f"  Bar chart   : {worst[0]} ({worst[1]}) is about {worst[1] / best[1]:.1f} times as polluted as {best[0]} ({best[1]}).")
    print(f"  Box plot    : the boxes do not overlap much, so the difference between stations is real and")
    print(f"                not just noise. Dots above the whiskers are the high-pollution spikes.")
    print(f"  Scatter     : correlation between temperature and PM2.5 is {corr:.2f}. Hotter hours tend to have")
    print(f"                lower PM2.5 in this data (cool nights trap pollution near the ground).")
    print(f"  Hour bars   : worst hour is {peak_hour[0]:02d}:00 ({peak_hour[1]:.1f}), cleanest is {low_hour[0]:02d}:00 ({low_hour[1]:.1f}).")
    print(f"                Morning (7-9) and evening (19-21) rush hours stand out.")
    print(f"  Histogram   : the readings spread over a wide range because the four stations sit at")
    print(f"                different levels, with a tail to the right. A few very bad hours pull the mean up,")
    print(f"                so the median is a safer centre than the mean.")
    con.close()


if __name__ == "__main__":
    part1()
    part2()
