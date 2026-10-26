"""Task 10 - Compare expectations with execution (K4 - Analyse).
float vs Decimal totals for 300, 6,000 and 150,000 payments, timing, rounding policy,
and the rate-table (dictionary) alternative."""
import random
import sys
import time
from decimal import Decimal as D

from milk_calculator import money, payout, rate_per_litre


def make_entries(n, litre_decimals=1, seed=2025):
    """n random but reproducible entries as strings: (litres, fat, snf)."""
    rnd = random.Random(seed)
    scale = 10 ** litre_decimals
    return [(f"{rnd.randint(2 * scale, 40 * scale) / scale:.{litre_decimals}f}",
             f"{rnd.randint(20, 70) / 10:.1f}", f"{rnd.randint(78, 95) / 10:.1f}") for _ in range(n)]


def float_rate(fat, snf):
    return 30.00 + round((fat - 3.5) / 0.1) * 0.40 + round((snf - 8.5) / 0.1) * 0.30


def compare(label, litre_decimals):
    print(f"\n##### DATASET {label} #####")
    print(f"{'n':>8} | {'BANK (Decimal, round each)':>27} | {'Decimal, round total only':>26} | {'float sum, no rounding':>24} | {'float, round each':>19}")
    rows = []
    for n in (300, 6000, 150000):
        entries = make_entries(n, litre_decimals)
        dec_entries = [(D(l), D(f), D(s)) for l, f, s in entries]
        flt_entries = [(float(l), float(f), float(s)) for l, f, s in entries]

        t0 = time.perf_counter()
        bank = sum((payout(l, f, s) for l, f, s in dec_entries), D("0"))
        t_dec = time.perf_counter() - t0
        total_only = money(sum((l * rate_per_litre(f, s) for l, f, s in dec_entries), D("0")))

        t0 = time.perf_counter()
        float_plain = 0.0
        for l, f, s in flt_entries:
            float_plain += l * float_rate(f, s)
        t_flt = time.perf_counter() - t0

        float_each = 0.0
        for l, f, s in flt_entries:
            float_each += round(l * round(float_rate(f, s), 2), 2)

        rows.append((n, bank, total_only, float_plain, float_each, t_dec, t_flt))
        print(f"{n:>8} | {str(bank):>27} | {str(total_only):>26} | {float_plain:>24.10f} | {float_each:>19.10f}")

    print(f"\n{'n':>8} | {'float plain - bank':>19} | {'float round-each - bank':>24} | {'round-total-only - bank':>24}")
    for n, bank, total_only, fp, fe, _, _ in rows:
        print(f"{n:>8} | {float(D(repr(fp)) - bank):>19.10f} | {float(D(repr(fe)) - bank):>24.10f} | {total_only - bank:>24}")

    print(f"\n{'n':>8} | {'Decimal time (ms)':>18} | {'float time (ms)':>16} | Decimal/float")
    for n, _, _, _, _, t_dec, t_flt in rows:
        print(f"{n:>8} | {t_dec * 1000:18.2f} | {t_flt * 1000:16.2f} | {t_dec / t_flt:6.1f}x")


print("Expectation: float and Decimal totals should agree. Bank amount = sum of EACH payment")
print("rounded to the paisa, computed with exact Decimal arithmetic.")
compare("A: litres read to 0.1 L (as at the centre today)", 1)
compare("B: litres read to 0.01 L (a finer weighing scale)", 2)

print("""
Observations and reasons
  1. float sums differ from the bank total by tiny fractions (about 1e-10 for 300 payments and
     about 1e-6 for 150,000): binary floats cannot store 0.1 or 0.40 exactly and the errors
     accumulate with n. Printed to 2 decimals they look right, but equality tests fail.
  2. Dataset A: litres has 1 decimal and every rate has 1 decimal, so each amount has at most
     2 decimals and NO rounding ever happens: rounding each payment or only the total gives the
     same bank amount. Dataset B (2-decimal litres): amounts can have 3 decimals, half-paise
     appear, and rounding only the total can differ from the bank. The bank rounds EACH
     payment, so the program must also round each payment and then add the rounded payments.
  3. In dataset B the totals are wrong by about Rs 0.16 (300 payments), Rs 2.56 (6,000) and
     Rs 64.58 (150,000) when only the total is rounded, and Rs 67.40 with float round() per
     payment: Python's round() sends ties to the EVEN digit while the bank rounds halves UP.
     The reason is therefore the ROUNDING RULE (half-up on each payment) and exact decimal
     arithmetic, not just float error.
  4. Decimal is about 4-8 times slower than float but exact; 150,000 payments still take a
     fraction of a second, so the cost is acceptable.""")

# ------------------------------------------------ alternative: rate table
print("\n=== ALTERNATIVE: rate table (dictionary) instead of recalculating ===")
print(f"{'n':>8} {'k pairs':>8} | {'recalculate (ms)':>17} | {'lookup (ms)':>12} | {'table build (ms)':>17} | {'dict bytes':>11}")
for n in (300, 6000, 150000):
    entries = make_entries(n)
    pairs = [(D(f), D(s)) for _, f, s in entries]
    t0 = time.perf_counter()
    r1 = [rate_per_litre(f, s) for f, s in pairs]
    t_re = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    table = {}
    for key in set(pairs):
        table[key] = rate_per_litre(*key)
    t_build = (time.perf_counter() - t0) * 1000
    t0 = time.perf_counter()
    r2 = [table[p] for p in pairs]
    t_look = (time.perf_counter() - t0) * 1000
    print(f"{n:>8} {len(table):>8} | {t_re:17.2f} | {t_look:12.2f} | {t_build:17.2f} | {sys.getsizeof(table):>11}")
    assert r1 == r2
print("""
Lookup is O(1) per entry on average and recalculation is O(1) per entry too, but the constant is
much larger for recalculation (several Decimal operations). The table costs O(k) extra space for
k distinct (fat, snf) pairs (here at most 51 fat values x 18 SNF values = 918 pairs, about 37 KB), and must be REBUILT
whenever the rate card changes. Worth it for 150,000 entries; pointless for 300.""")
