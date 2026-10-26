"""Task 1 - Understand the problem and identify the data (K4 - Analyse).

Prints the data analysis (inputs, outputs, constants, types, rules, assumptions)
and then demonstrates the 'Alternative Concept': three separate variables per
farmer versus one tuple per entry kept in a list.
"""
import sys
import time

# ---------------------------------------------------------------- analysis
INPUTS = [
    # name,        python type, kind,       justification
    ("farmer_id", "str",   "text",       "Codes like 'F017' or '0042'; leading zeros must survive, never used in arithmetic"),
    ("shift",     "str",   "text",       "'M' (morning) or 'E' (evening); a label, not a number"),
    ("litres",    "Decimal", "fractional", "Quantity can be 8.5 L; must be exact because money depends on it"),
    ("fat",       "Decimal", "fractional", "Fat % e.g. 4.2; compared in 0.1 steps, so binary float errors matter"),
    ("snf",       "Decimal", "fractional", "SNF % e.g. 8.7; same reason as fat"),
]
OUTPUTS = [
    ("rate_per_litre", "Decimal", "fractional", "Rs/litre after fat and SNF adjustment, 2 decimals"),
    ("amount",         "Decimal", "fractional", "litres x rate, rounded to the paisa (2 decimals)"),
    ("ten_day_total",  "Decimal", "fractional", "Sum of the rounded amounts of one farmer in 10 days"),
    ("entry_count",    "int",     "whole",      "How many entries were processed (counting only)"),
]
CONSTANTS = [
    ("BASE_RATE",      "30.00", "Rs/litre at 3.5% fat and 8.5% SNF"),
    ("STANDARD_FAT",   "3.5",   "reference fat %"),
    ("STANDARD_SNF",   "8.5",   "reference SNF %"),
    ("STEP",           "0.1",   "size of one fat/SNF step in %"),
    ("FAT_STEP_VALUE", "0.40",  "Rs/litre per fat step"),
    ("SNF_STEP_VALUE", "0.30",  "Rs/litre per SNF step"),
    ("MIN_FAT / MAX_FAT", "2.0 / 7.0", "valid fat range"),
    ("MIN_SNF / MAX_SNF", "7.0 / 10.0", "valid SNF range (assumption)"),
    ("PAYMENT_DAYS",   "10",    "settlement cycle in days"),
]
RULES = [
    "litres must be a number greater than 0 (no negative or zero quantity)",
    "fat must satisfy 2.0 <= fat <= 7.0 (outside = analyser/clerk error or adulteration)",
    "snf must satisfy 7.0 <= snf <= 10.0 (assumed range)",
    "shift must be 'M' or 'E'",
    "farmer_id must not be empty",
    "rate per litre and amount are rounded to 2 decimals (paisa) with ROUND_HALF_UP",
    "the ten-day total is the SUM OF THE ROUNDED PAYMENTS (that is what the bank pays)",
]
ASSUMPTIONS = [
    "fat and SNF are read to ONE decimal place at the centre (the analyser comes later in Task 12)",
    "half-paisa is rounded up (ROUND_HALF_UP), the usual accounting rule",
    "a fat/SNF step is counted to the NEAREST whole 0.1 step",
    "one entry = one farmer, one shift; a farmer may have up to 20 entries in 10 days",
    "SNF limits 7.0-10.0 are not given in the question, so they are an assumption",
]


def show(title, rows):
    print(f"\n{title}")
    print("-" * len(title))
    for row in rows:
        print("  " + " | ".join(str(x) for x in row))


print("TASK 1 - PROBLEM ANALYSIS")
show("INPUTS (name | type | kind | why)", INPUTS)
show("OUTPUTS (name | type | kind | why)", OUTPUTS)
show("NAMED CONSTANTS (name | value | meaning)", CONSTANTS)
print("\nRULES every correct payment must satisfy")
print("-" * 40)
for i, r in enumerate(RULES, 1):
    print(f"  R{i}. {r}")
print("\nASSUMPTIONS")
print("-" * 11)
for i, a in enumerate(ASSUMPTIONS, 1):
    print(f"  A{i}. {a}")

# ------------------------------------------------ alternative concept demo
print("\n\n=== ALTERNATIVE CONCEPT: separate variables vs one tuple per entry ===")


def rate(fat, snf):
    return 30.0 + round((fat - 3.5) / 0.1) * 0.40 + round((snf - 8.5) / 0.1) * 0.30


def source_with_separate_variables(n):
    """Return Python source code a programmer would have to write for n farmers."""
    lines = []
    for i in range(1, n + 1):
        lines.append(f"litres{i}, fat{i}, snf{i} = {i % 20 + 1}, 3.5, 8.5")
    lines.append("total = 0.0")
    for i in range(1, n + 1):
        lines.append(f"total += litres{i} * rate(fat{i}, snf{i})")
    return "\n".join(lines)


print("\nDesign A: litres1, fat1, snf1, litres2, ... (three names per farmer)")
for n in (300, 6000):
    src = source_with_separate_variables(n)
    t0 = time.perf_counter()
    namespace = {"rate": rate}
    exec(compile(src, "<generated>", "exec"), namespace)
    elapsed = time.perf_counter() - t0
    print(f"  n={n:>6}: {len(src.splitlines()):>6} lines of source, {3 * n:>6} variable names, "
          f"compile+run {elapsed * 1000:8.2f} ms, total = {namespace['total']:.2f}")
print("  n=150000 would need 450,000 variable names and ~300,000 hand-written lines: not practical.")
print("  Adding ONE more farmer means EDITING THE PROGRAM (new names, new line).")

print("\nDesign B: one tuple per entry inside a list, one loop for any n")
entries_300 = [(i % 20 + 1, 3.5, 8.5) for i in range(1, 301)]
total = 0.0
for litres, fat, snf in entries_300:
    total += litres * rate(fat, snf)
print(f"  n=300 total = {total:.2f}  (same answer as design A, 3 lines of code)")

print("\nTime and space of Design B (loop with a list of tuples):")
print(f"  {'n':>8} {'time (ms)':>12} {'list size (bytes)':>20}")
for n in (300, 6000, 150000):
    data = [(i % 20 + 1, 3.5, 8.5) for i in range(1, n + 1)]
    t0 = time.perf_counter()
    total = 0.0
    for litres, fat, snf in data:
        total += litres * rate(fat, snf)
    elapsed = (time.perf_counter() - t0) * 1000
    print(f"  {n:>8} {elapsed:12.2f} {sys.getsizeof(data):20}")

print("""
Complexity
  Both designs do the same arithmetic per entry, so TIME is O(n) for both.
  SPACE: both store 3n numbers = O(n) data, BUT design A also needs 3n distinct
  NAMES in the program text (source size O(n), a symbol table of 3n entries) and
  its CODE must grow with n; design B's code is O(1) in size. Only design B scales:
  the program does not change when the number of farmers changes.""")
