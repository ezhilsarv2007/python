# B2 - adversarial data: bad files, SQL injection, tricky sentences
import csv
import io
import os
import sqlite3
import time

from sentiment import label, score

HERE = os.path.dirname(os.path.abspath(__file__))
FOLDER = os.path.join(HERE, "adversarial_files")
os.makedirs(FOLDER, exist_ok=True)

REQUIRED = ["station", "date", "hour", "pm25"]


# ------------------------------------------------------------------
# 1. bad files
# ------------------------------------------------------------------
def make_bad_files():
    good = "station,date,hour,pm25\nKílpauk,2026-10-01,8,64\nAdyar,2026-10-01,8,48\n"
    files = {
        "missing_column.csv": "station,date,hour\nAdyar,2026-10-01,8\n",
        "wrong_delimiter.csv": "station;date;hour;pm25\nAdyar;2026-10-01;8;48\n",
        "empty.csv": "",
    }
    for name, text in files.items():
        with open(os.path.join(FOLDER, name), "w", encoding="utf-8", newline="") as f:
            f.write(text)
    with open(os.path.join(FOLDER, "cp1252_encoding.csv"), "w", encoding="cp1252", newline="") as f:
        f.write(good)                       # the i with an accent is stored as one byte
    with open(os.path.join(FOLDER, "utf16_encoding.csv"), "w", encoding="utf-16", newline="") as f:
        f.write(good)
    return sorted(os.listdir(FOLDER))


def naive_load(path):
    """What a first version of the program would do."""
    with open(path, encoding="utf-8", newline="") as f:
        return [(r["station"], r["date"], int(r["hour"]), float(r["pm25"])) for r in csv.DictReader(f)]


def safe_load(path):
    """Checks everything before trusting the file. Raises ValueError with a clear message."""
    raw = open(path, "rb").read()
    if not raw.strip():
        raise ValueError("file is empty")
    # try encodings in order; utf-16 files start with a byte-order mark
    for enc in ("utf-8-sig", "utf-16", "cp1252"):
        try:
            text = raw.decode(enc)
            used = enc
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("cannot decode the file with utf-8, utf-16 or cp1252")
    header = text.splitlines()[0]
    try:
        delimiter = csv.Sniffer().sniff(header, delimiters=",;\t|").delimiter
    except csv.Error:
        delimiter = ","
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
    if missing:
        raise ValueError(f"missing column(s): {missing}; header was {reader.fieldnames}")
    rows = [(r["station"], r["date"], int(r["hour"]), float(r["pm25"])) for r in reader]
    return rows, used, delimiter


def part_files():
    print("=" * 70)
    print("1. BAD FILES: naive loader vs safe loader")
    print("=" * 70)
    for name in make_bad_files():
        path = os.path.join(FOLDER, name)
        print(f"\n{name}")
        try:
            print("   naive :", naive_load(path))
        except Exception as e:
            print(f"   naive : {type(e).__name__}: {e}")
        try:
            rows, enc, delim = safe_load(path)
            print(f"   safe  : OK, encoding={enc}, delimiter={delim!r}, rows={rows}")
        except ValueError as e:
            print(f"   safe  : rejected cleanly -> {e}")


# ------------------------------------------------------------------
# 2. SQL injection
# ------------------------------------------------------------------
def part_sql():
    print("\n" + "=" * 70)
    print("2. STATION NAMES WITH A QUOTE: string building vs ? placeholder")
    print("=" * 70)
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE aq (station TEXT, pm25 REAL)")
    con.executemany("INSERT INTO aq VALUES (?, ?)",
                    [("Adyar", 48), ("Adyar", 60), ("Guindy", 95), ("Guindy", 121), ("St. Mary's Road", 70)])
    con.commit()

    def with_plus(name):
        sql = "SELECT AVG(pm25) FROM aq WHERE station = '" + name + "'"
        return sql, con.execute(sql).fetchone()[0]

    def with_placeholder(name):
        return con.execute("SELECT AVG(pm25) FROM aq WHERE station = ?", (name,)).fetchone()[0]

    for name in ["Adyar", "St. Mary's Road", "Adyar' OR '1'='1"]:
        print(f"\ninput: {name!r}")
        try:
            sql, result = with_plus(name)
            print("   + version  SQL  :", sql)
            print("   + version  gives:", result)
        except sqlite3.Error as e:
            print(f"   + version  FAILED: {type(e).__name__}: {e}")
        print("   ? version  gives:", with_placeholder(name))
    print("\nReading the results:")
    print("  - the real name 'St. Mary's Road' breaks the + version (the quote ends the string early)")
    print("    but works with ?, because the value is never pasted into the SQL text")
    print("  - the injection text changes the meaning of the + query: it returns the average of ALL rows")
    print("    (data the user should not be able to reach); with ? it is just a station name that does")
    print("    not exist, so the answer is None")

    # a stacked statement attempt
    try:
        con.execute("SELECT 1; DROP TABLE aq")
    except Exception as e:
        print(f"  - sqlite3's execute() refuses stacked statements: {type(e).__name__}: {e}")
    con.close()

    print("\nexecutemany() vs execute() in a loop (in-memory table, one commit at the end):")
    print(f"  {'rows':>8} {'loop':>10} {'executemany':>12}")
    for n in (10_000, 100_000, 500_000):
        data = [("S%d" % (i % 12), float(i % 200)) for i in range(n)]
        c1 = sqlite3.connect(":memory:"); c1.execute("CREATE TABLE t (s TEXT, v REAL)")
        t = time.perf_counter()
        for row in data:
            c1.execute("INSERT INTO t VALUES (?, ?)", row)
        c1.commit(); loop_t = time.perf_counter() - t
        c2 = sqlite3.connect(":memory:"); c2.execute("CREATE TABLE t (s TEXT, v REAL)")
        t = time.perf_counter()
        c2.executemany("INSERT INTO t VALUES (?, ?)", data)
        c2.commit(); many_t = time.perf_counter() - t
        print(f"  {n:>8} {loop_t:>9.3f}s {many_t:>11.3f}s")
        c1.close(); c2.close()
    print("  both are O(n); executemany is faster by a constant factor because the loop pays Python call")
    print("  overhead for every row")


# ------------------------------------------------------------------
# 3. sentiment scorer vs tricky sentences
# ------------------------------------------------------------------
TRICKY = [
    # (type, sentence, what a human would say)
    ("sarcasm", "Oh great, another smoky day. Just wonderful.", "negative"),
    ("sarcasm", "Thanks a lot for ignoring our complaint again.", "negative"),
    ("sarcasm", "Fantastic, the air smells like a bonfire.", "negative"),
    ("double negative", "The staff were never not helpful.", "positive"),
    ("double negative", "I cannot say the service was not good.", "positive"),
    ("negator too far", "The bus was not very good.", "negative"),
    ("negator too far", "The air is not at all clean.", "negative"),
    ("mixed", "Staff were helpful but the burning smell and noise are terrible.", "mixed"),
    ("mixed", "Roads are clean and the bus is fast but the air is toxic and smoky.", "mixed"),
    ("works", "No smoke today, air is clean.", "positive"),
    ("works", "The new bus service wasn't bad.", "positive"),
    ("works", "The factory smoke is choking us.", "negative"),
    ("unknown words", "Bro the AQI is cooked, absolutely lit up red.", "negative"),
]


def part_sentiment():
    print("\n" + "=" * 70)
    print("3. SENTIMENT SCORER vs TRICKY SENTENCES")
    print("=" * 70)
    fails = 0
    for kind, text, truth in TRICKY:
        got = label(text)
        ok = got == truth
        fails += (not ok)
        print(f"\n[{kind}] {text}")
        print(f"   score={score(text):+d}  scorer says: {got:<8} human says: {truth:<8} -> {'OK' if ok else 'FAIL'}")
    print(f"\nScorer was wrong on {fails} of {len(TRICKY)} sentences.")


if __name__ == "__main__":
    part_files()
    part_sql()
    part_sentiment()
