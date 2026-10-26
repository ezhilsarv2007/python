"""Ksheera Milk Co-operative - payment calculator (final design, Tasks 9-11).

All money is Decimal; all rates live in the constants below (one place to revise).
Run:   python milk_calculator.py --file entries.csv     (process a file of entries)
       python milk_calculator.py                        (type entries one by one)
"""
import csv
import sys
from decimal import Decimal, ROUND_HALF_UP

# ------------------------------------------------------------------ constants
BASE_RATE = Decimal("30.00")        # Rs/litre at 3.5 % fat and 8.5 % SNF
STANDARD_FAT = Decimal("3.5")
STANDARD_SNF = Decimal("8.5")
STEP = Decimal("0.1")               # one step = 0.1 %
FAT_STEP_VALUE = Decimal("0.40")    # Rs/litre per fat step
SNF_STEP_VALUE = Decimal("0.30")    # Rs/litre per SNF step
MIN_FAT, MAX_FAT = Decimal("2.0"), Decimal("7.0")
MIN_SNF, MAX_SNF = Decimal("7.0"), Decimal("10.0")      # assumption
MAX_LITRES = Decimal("1000")                            # assumption: sanity limit per entry
SHIFTS = ("M", "E")
PAISA = Decimal("0.01")


class InvalidEntry(ValueError):
    """Raised when a clerk's entry breaks a rule."""


# ------------------------------------------------------------------ helpers
def money(value):
    """Round a Decimal to the paisa, halves rounded UP (accounting rule)."""
    return value.quantize(PAISA, rounding=ROUND_HALF_UP)


def parse_decimal(text, name):
    """Convert clerk text to Decimal using str checks; raise InvalidEntry otherwise."""
    t = str(text).strip()
    if t == "" or t.count(".") > 1 or not t.replace(".", "", 1).isdigit():
        raise InvalidEntry(f"{name} '{text}' is not a valid positive number")
    return Decimal(t)


def count_steps(value, standard):
    """Number of 0.1 % steps (whole number, nearest) of value above/below standard."""
    return ((value - standard) / STEP).to_integral_value(rounding=ROUND_HALF_UP)


def rate_per_litre(fat, snf):
    """Rate in Rs/litre (Decimal, paisa) for Decimal fat % and SNF %."""
    rate = BASE_RATE + count_steps(fat, STANDARD_FAT) * FAT_STEP_VALUE \
        + count_steps(snf, STANDARD_SNF) * SNF_STEP_VALUE
    return money(rate)


def payout(litres, fat, snf):
    """Amount payable in Rs (Decimal, paisa) = litres x rate, rounded once."""
    return money(litres * rate_per_litre(fat, snf))


def validate_entry(farmer_id, shift, litres_text, fat_text, snf_text):
    """Check one raw entry and return (farmer_id, shift, litres, fat, snf) as Decimals.

    Raises InvalidEntry with a clear reason for the first rule that is broken.
    """
    farmer_id = str(farmer_id).strip()
    shift = str(shift).strip().upper()
    if farmer_id == "":
        raise InvalidEntry("farmer id is empty")
    if shift not in SHIFTS:
        raise InvalidEntry(f"shift '{shift}' must be M or E")
    litres = parse_decimal(litres_text, "litres")
    fat = parse_decimal(fat_text, "fat")
    snf = parse_decimal(snf_text, "snf")
    if not 0 < litres <= MAX_LITRES:
        raise InvalidEntry(f"litres {litres} must be > 0 and <= {MAX_LITRES}")
    if not MIN_FAT <= fat <= MAX_FAT:
        raise InvalidEntry(f"fat {fat} must be between {MIN_FAT} and {MAX_FAT}")
    if not MIN_SNF <= snf <= MAX_SNF:
        raise InvalidEntry(f"snf {snf} must be between {MIN_SNF} and {MAX_SNF}")
    return farmer_id, shift, litres, fat, snf


def process_rows(rows):
    """Process an iterable of (farmer_id, shift, litres, fat, snf) text rows.

    Prints a neat report, and returns (totals_per_farmer, grand_total, rejected_count).
    """
    totals, rejected = {}, 0
    print(f"{'Line':>4} {'Farmer':<8}{'Sh':<4}{'Litres':>9}{'Fat':>6}{'SNF':>6}{'Rate':>9}{'Amount':>11}")
    print("-" * 58)
    for line_no, row in enumerate(rows, start=1):
        try:
            if len(row) != 5:
                raise InvalidEntry(f"expected 5 fields but found {len(row)} (a comma typed inside a number?)")
            farmer_id, shift, litres, fat, snf = validate_entry(*row)
        except InvalidEntry as err:
            rejected += 1
            print(f"{line_no:>4} REJECTED {list(row)} -> {err}")
            continue
        rate = rate_per_litre(fat, snf)
        amount = payout(litres, fat, snf)
        totals[farmer_id] = totals.get(farmer_id, Decimal("0")) + amount
        print(f"{line_no:>4} {farmer_id:<8}{shift:<4}{litres:9.2f}{fat:6.1f}{snf:6.1f}{rate:9.2f}{amount:11.2f}")
    grand = sum(totals.values(), Decimal("0"))
    print("\nTEN-DAY TOTAL PER FARMER")
    for farmer_id in sorted(totals):
        print(f"  {farmer_id:<8}{totals[farmer_id]:12.2f}")
    print(f"  {'TOTAL':<8}{grand:12.2f}      (rejected entries: {rejected})")
    return totals, grand, rejected


def read_csv(path):
    """Yield (farmer_id, shift, litres, fat, snf) rows from a CSV file with a header."""
    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader)                      # skip header
        for row in reader:
            yield tuple(row)


def main():
    if "--file" in sys.argv:
        process_rows(list(read_csv(sys.argv[sys.argv.index("--file") + 1])))
        return
    print("Enter entries (blank farmer id to finish)")
    rows = []
    while True:
        farmer_id = input("Farmer id: ")
        if farmer_id.strip() == "":
            break
        rows.append((farmer_id, input("Shift (M/E): "), input("Litres: "), input("Fat %: "), input("SNF %: ")))
    process_rows(rows)


if __name__ == "__main__":
    main()
