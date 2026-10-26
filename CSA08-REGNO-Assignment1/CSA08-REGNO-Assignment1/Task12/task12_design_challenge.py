"""Task 12 - Day-4 design challenge: re-evaluate and adapt (K5 - Evaluate)."""
from datetime import date
from decimal import Decimal as D

import milkrate_original as old
import milkrate_v2 as new

MAR, MAY = date(2025, 3, 15), date(2025, 5, 15)

print("=" * 78)
print("A. IMPACT ANALYSIS")
print("=" * 78)
print("""What changed
  1. Analyser readings now have TWO decimals (fat 4.25, snf 8.55) - before: one decimal.
  2. Seasonal card: Apr-Jun base Rs 32.00 and fat step Rs 0.45 (SNF step stays Rs 0.30).
  3. NEW rule at the ten-day level: > 500 L in ten days earns Rs 0.50 per litre bonus.
Affected parts of the original design
  constants   : BASE_RATE and FAT_STEP_VALUE are no longer single values -> one RateCard per season.
  expressions : round((fat - 3.5) / 0.1) assumed 1-decimal data; now (4.25 - 3.5)/0.1 = 7.5 steps.
  functions   : rate_per_litre(fat, snf) has no way to know the date/season; payout() likewise.
  new         : a bonus function needing the TEN-DAY litres, which no per-entry function has.
  module      : milkrate.py still imports fine but now holds only the normal card.""")

print("Two-decimal readings and the step count (fat 4.25, snf 8.55):")
print("  exact steps          : fat", (D("4.25") - D("3.5")) / D("0.1"), " snf", (D("8.55") - D("8.5")) / D("0.1"))
print("  round() (original)   : fat", round((4.25 - 3.5) / 0.1), " snf", round((8.55 - 8.5) / 0.1),
      " <- every x.5 step is a TIE: float noise and ties-to-even decide the result, not a rule")

print()
print("=" * 78)
print("B. EVALUATION OF THE ORIGINAL DESIGN (worked examples with the new readings)")
print("=" * 78)
cases = [(10, "4.25", "8.55"), (10, "3.55", "8.45"), (10, "3.75", "8.5"), (10, "3.45", "8.5")]
print(f"{'litres':>6} {'fat':>5} {'snf':>5} | {'original (normal card)':>23} | {'new, normal card':>17} | {'difference':>10}")
for litres, fat, snf in cases:
    o = old.rate_per_litre(float(fat), float(snf))
    n = new.rate_per_litre(D(fat), D(snf), new.NORMAL)
    print(f"{litres:>6} {fat:>5} {snf:>5} | {o:>23.2f} | {n:>17} | {D(str(o)) - n:>10}")
print("""Verdict on the original parts
  RETAIN : constants in ONE place, small functions with docstrings, Decimal for money,
           'round each payment' rule, validation, assert-based tests, module structure.
  FAIL   : float + round() mishandles 2-decimal readings (a half step is a tie: fat 3.75 is
           rounded DOWN to 2 steps and fat 3.45 to 0 steps, so farmers lose or gain Rs 0.20-0.35
           per litre); no season; no ten-day bonus.
  => MODIFY (not redesign, not retain): the architecture is sound, three pieces change.""")

print()
print("=" * 78)
print("C. ADAPTATION - milkrate_v2.py (RateCard + select_rate_card + payout(date) + bonus())")
print("=" * 78)
print("select_rate_card(15 Mar) ->", new.select_rate_card(MAR).name)
print("select_rate_card(15 May) ->", new.select_rate_card(MAY).name)
print("rate(4.25, 8.55) normal  ->", new.rate_per_litre(D("4.25"), D("8.55"), new.NORMAL))
print("rate(4.25, 8.55) summer  ->", new.rate_per_litre(D("4.25"), D("8.55"), new.SUMMER),
      " (32.00 + 7.5 x 0.45 + 0.5 x 0.30 = 35.525 -> 35.53)")
print("bonus(550 L) ->", new.bonus(D("550")), "| bonus(500 L) ->", new.bonus(D("500")), "| bonus(500.1 L) ->", new.bonus(D("500.1")))

print()
print("=" * 78)
print("D. EVIDENCE-BASED DEFENCE - tests for both seasons and the bonus")
print("=" * 78)
TESTS = [
    # name, litres, fat, snf, date, expected rate, expected amount
    ("normal season, standard milk",     "10",  "3.5",  "8.5",  MAR, "30.00", "300.00"),
    ("normal season, sample 2",          "8.5", "4.2",  "8.7",  MAR, "33.40", "283.90"),
    ("normal season, sample 3",          "12",  "3.1",  "8.3",  MAR, "27.80", "333.60"),
    ("summer, standard milk",            "10",  "3.5",  "8.5",  MAY, "32.00", "320.00"),
    ("summer, fat 4.2 snf 8.7",          "8.5", "4.2",  "8.7",  MAY, "35.75", "303.88"),
    ("summer, fat 3.1 snf 8.3",          "12",  "3.1",  "8.3",  MAY, "29.60", "355.20"),
    ("summer, 2-decimal 4.25 / 8.55",    "10",  "4.25", "8.55", MAY, "35.53", "355.30"),
    ("normal, 2-decimal 3.75 / 8.5",     "10",  "3.75", "8.5",  MAR, "31.00", "310.00"),
    ("first day of summer (1 Apr)",      "10",  "3.5",  "8.5",  date(2025, 4, 1), "32.00", "320.00"),
    ("last day of summer (30 Jun)",      "10",  "3.5",  "8.5",  date(2025, 6, 30), "32.00", "320.00"),
    ("day after summer (1 Jul)",         "10",  "3.5",  "8.5",  date(2025, 7, 1), "30.00", "300.00"),
]
passed = 0
print(f"{'Test':<34}{'Exp rate':>9}{'Act rate':>9}{'Exp amt':>9}{'Act amt':>9}  Result")
for name, litres, fat, snf, d, exp_rate, exp_amt in TESTS:
    rate = new.rate_per_litre(D(fat), D(snf), new.select_rate_card(d))
    amt = new.payout(D(litres), D(fat), D(snf), d)
    ok = rate == D(exp_rate) and amt == D(exp_amt)
    passed += ok
    print(f"{name:<34}{exp_rate:>9}{str(rate):>9}{exp_amt:>9}{str(amt):>9}  {'PASS' if ok else 'FAIL'}")
    assert ok, name

print("\nTen-day bonus tests (summer, standard milk, rate 32.00)")
print(f"{'Test':<34}{'litres':>8}{'payments':>11}{'bonus':>9}{'grand total':>13}  Result")
BONUS_TESTS = [
    ("55 entries x 10 L = 550 L",      55, "10",    "17600.00", "275.00"),
    ("exactly 500 L: NO bonus",        50, "10",    "16000.00",              "0.00"),
    ("500.1 L: bonus on all litres",    1, "500.1", "16003.20",              "250.05"),
    ("small farmer 30 L: no bonus",     3, "10",    "960.00",                "0.00"),
]
for name, count, litres, exp_pay, exp_bonus in BONUS_TESTS:
    entries = [(MAY, D(litres), D("3.5"), D("8.5"))] * count
    total_l, pay, b, grand = new.ten_day_statement(entries)
    ok = pay == D(exp_pay) and b == D(exp_bonus) and grand == D(exp_pay) + D(exp_bonus)
    passed += ok
    print(f"{name:<34}{str(total_l):>8}{str(pay):>11}{str(b):>9}{str(grand):>13}  {'PASS' if ok else 'FAIL'}")
    assert ok, name

print("\nMixed ten days across the season boundary (28 Mar - 6 Apr style): each entry uses ITS date's card")
mixed = [(date(2025, 3, 30), D("10"), D("3.5"), D("8.5")), (date(2025, 4, 2), D("10"), D("3.5"), D("8.5"))]
_, pay, b, grand = new.ten_day_statement(mixed)
assert pay == D("620.00") and b == D("0.00")
print(f"  300.00 (Mar) + 320.00 (Apr) = {pay}  PASS")
passed += 1
print(f"\nSUMMARY: {passed} tests passed, 0 failed")

print("""
Trade-offs and defence of MODIFY
  + Re-uses the tested core (Decimal, round each payment, validation); only 3 pieces change.
  + A new season = one new RateCard line; the bonus = one constant pair; no copy-paste of formulas.
  + Fractional steps pro-rate 2-decimal readings fairly and need no rounding of steps at all.
  - Pro-rating changes amounts versus the old method for 2-decimal data (see section B): the union
    must confirm that fractional steps are intended.
  - Assumptions to confirm: bonus on ALL litres once > 500 L, in every season; bonus not rounded
    per entry but once per ten days; seasons by calendar month of each entry.
  - A redesign (database, rules engine) would be over-engineering for 150,000 farmers and
    four rules; RETAIN would leave wrong payments, so MODIFY is the evidence-based choice.""")
