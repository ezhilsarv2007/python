import csv
import io

RAW = """station,date,pm25
Adyar,2026-10-01,48
Adyar,2026-10-02,NA
Adyar,2026-10-03,
Guindy,2026-10-01,95
Guindy,2026-10-02,-5
Guindy,2026-10-03,121
"""

# readings above this are treated as sensor faults
MAX_PM25 = 999


def load_clean(text):
    """Returns (station, date, pm25) tuples for valid, non-negative readings only."""
    rows = []
    # TODO 1: Read the text with csv.DictReader; skip rows whose pm25 is empty, 'NA' or
    #   negative; convert pm25 to float
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        raw = row["pm25"].strip()
        if raw == "" or raw.upper() == "NA":
            continue
        value = float(raw)
        if value < 0 or value > MAX_PM25:      # extra check asked in the question
            continue
        rows.append((row["station"], row["date"], value))
    return rows


def min_max(values):
    # TODO 2: Scale each value to the range 0-1 using (v - min) / (max - min), rounded
    #   to 3 decimals
    lo, hi = min(values), max(values)
    if hi == lo:                                # all values same, avoid dividing by zero
        return [0.0 for _ in values]
    return [round((v - lo) / (hi - lo), 3) for v in values]


clean = load_clean(RAW)
print(clean)
print(min_max([pm for _, _, pm in clean]))

# extra test: a row above 999 must be skipped
TEST = RAW + "Adyar,2026-10-04,1500\n"
print("with the 1500 row added :", load_clean(TEST))
print("1500 row skipped        :", len(load_clean(TEST)) == len(clean))
