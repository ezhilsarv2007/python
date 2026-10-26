"""Tests for milk_calculator.py: assert-based, prints a test table (Task 9).
Run:  python test_milk_calculator.py"""
from decimal import Decimal as D

from milk_calculator import InvalidEntry, payout, rate_per_litre, validate_entry

# ---- (case, litres, fat, snf, expected rate, expected amount) - all worked out by hand
VALID = [
    ("standard milk (3.5/8.5)",      "10",   "3.5", "8.5", "30.00", "300.00"),
    ("fat above standard",           "10",   "4.0", "8.5", "32.00", "320.00"),
    ("fat below standard",           "10",   "3.0", "8.5", "28.00", "280.00"),
    ("SNF above standard",           "10",   "3.5", "9.0", "31.50", "315.00"),
    ("SNF below standard",           "10",   "3.5", "8.0", "28.50", "285.00"),
    ("both above (sample 2)",        "8.5",  "4.2", "8.7", "33.40", "283.90"),
    ("both below (sample 3)",        "12",   "3.1", "8.3", "27.80", "333.60"),
    ("lowest allowed fat 2.0",       "10",   "2.0", "8.5", "24.00", "240.00"),
    ("highest allowed fat 7.0",      "10",   "7.0", "8.5", "44.00", "440.00"),
    ("lowest allowed SNF 7.0",       "10",   "3.5", "7.0", "25.50", "255.00"),
    ("highest allowed SNF 10.0",     "10",   "3.5", "10.0", "34.50", "345.00"),
    ("smallest litres 0.1",          "0.1",  "3.5", "8.5", "30.00", "3.00"),
    ("half-paisa rounds up",         "0.5",  "3.5", "8.3", "29.40", "14.70"),
]
INVALID = [
    ("text litres",            ("F1", "M", "eight", "3.5", "8.5")),
    ("comma decimal '8,5'",    ("F1", "M", "8,5", "3.5", "8.5")),
    ("empty litres",           ("F1", "M", "", "3.5", "8.5")),
    ("negative litres",        ("F1", "M", "-5", "3.5", "8.5")),
    ("zero litres",            ("F1", "M", "0", "3.5", "8.5")),
    ("fat below 2.0 (1.9)",    ("F1", "M", "10", "1.9", "8.5")),
    ("fat above 7.0 (7.1)",    ("F1", "M", "10", "7.1", "8.5")),
    ("snf out of range",       ("F1", "M", "10", "3.5", "10.1")),
    ("'nan' as fat",           ("F1", "M", "10", "nan", "8.5")),
    ("'1e2' as litres",        ("F1", "M", "1e2", "3.5", "8.5")),
    ("bad shift",              ("F1", "X", "10", "3.5", "8.5")),
    ("empty farmer id",        ("", "M", "10", "3.5", "8.5")),
]
HAND_SET = [("10", "3.5", "8.5"), ("8.5", "4.2", "8.7"), ("12", "3.1", "8.3"),
            ("20", "4.0", "8.5"), ("15.5", "3.0", "8.2")]
HAND_TOTAL = D("1977.55")      # 300.00 + 283.90 + 333.60 + 640.00 + 420.05

passed = failed = 0
print(f"{'#':>2} {'Test case':<28}{'Input (L, fat, snf)':<22}{'Exp rate':>9}{'Act rate':>9}{'Exp amt':>9}{'Act amt':>9}  Result")
print("-" * 100)
for i, (name, litres, fat, snf, exp_rate, exp_amt) in enumerate(VALID, 1):
    act_rate = rate_per_litre(D(fat), D(snf))
    act_amt = payout(D(litres), D(fat), D(snf))
    ok = act_rate == D(exp_rate) and act_amt == D(exp_amt)
    passed, failed = passed + ok, failed + (not ok)
    print(f"{i:>2} {name:<28}{litres + ', ' + fat + ', ' + snf:<22}{exp_rate:>9}{act_rate:>9}{exp_amt:>9}{act_amt:>9}  {'PASS' if ok else 'FAIL'}")
    assert ok, name

print(f"\n{'#':>2} {'Invalid entry case':<28}{'Expected':<22}{'Actual (reason)'}")
print("-" * 100)
for i, (name, entry) in enumerate(INVALID, 1):
    try:
        validate_entry(*entry)
        result, ok = "ACCEPTED (wrong!)", False
    except InvalidEntry as err:
        result, ok = f"rejected: {err}", True
    passed, failed = passed + ok, failed + (not ok)
    print(f"{i:>2} {name:<28}{'rejected':<22}{result}   {'PASS' if ok else 'FAIL'}")
    assert ok, name

hand_actual = sum((payout(D(l), D(f), D(s)) for l, f, s in HAND_SET), D("0"))
ok = hand_actual == HAND_TOTAL
passed, failed = passed + ok, failed + (not ok)
print(f"\nHand-calculated set of 5 entries: expected {HAND_TOTAL}, actual {hand_actual}  {'PASS' if ok else 'FAIL'}")
assert ok

print(f"\nSUMMARY: {passed} passed, {failed} failed, {passed + failed} tests")
assert failed == 0
print("All assert statements passed.")
