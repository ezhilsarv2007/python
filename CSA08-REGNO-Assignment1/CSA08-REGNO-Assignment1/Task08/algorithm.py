"""Task 8 - Python version of the pseudocode, hand trace check and the two total strategies."""
import time
import tracemalloc
from decimal import Decimal as D, ROUND_HALF_UP

BASE_RATE, FAT_STEP_VALUE, SNF_STEP_VALUE = D("30.00"), D("0.40"), D("0.30")


def one_payment(litres, fat, snf, trace=False):
    """Pseudocode A. Returns the amount, or None for an invalid entry."""
    if litres <= 0 or not D("2.0") <= fat <= D("7.0") or not D("7.0") <= snf <= D("10.0"):
        return None
    fat_steps = ((fat - D("3.5")) / D("0.1")).to_integral_value(ROUND_HALF_UP)
    snf_steps = ((snf - D("8.5")) / D("0.1")).to_integral_value(ROUND_HALF_UP)
    rate = BASE_RATE + fat_steps * FAT_STEP_VALUE + snf_steps * SNF_STEP_VALUE
    amount = (litres * rate).quantize(D("0.01"), ROUND_HALF_UP)
    if trace:
        print(f"      fat steps {fat_steps:+}, snf steps {snf_steps:+}, rate {rate}, amount {amount}")
    return amount


def total_running(entries):
    """Pseudocode B: keeps only a running total  -> O(n) time, O(1) extra space."""
    total = D("0")
    for litres, fat, snf in entries:
        amount = one_payment(litres, fat, snf)
        if amount is not None:
            total += amount
    return total


def total_stored(entries):
    """Stores every payment in a list and adds at the end -> O(n) time, O(n) extra space."""
    amounts = []
    for litres, fat, snf in entries:
        amount = one_payment(litres, fat, snf)
        if amount is not None:
            amounts.append(amount)
    return sum(amounts, D("0")), amounts


print("=== Hand-trace check (compare with pseudocode.md) ===")
week = [(D("10"), D("3.5"), D("8.5")), (D("8.5"), D("4.2"), D("8.7")), (D("12"), D("3.1"), D("8.3"))]
running = D("0")
for i, (litres, fat, snf) in enumerate(week, 1):
    print(f"  step {i}: litres={litres} fat={fat} snf={snf}")
    amount = one_payment(litres, fat, snf, trace=True)
    running += amount
    print(f"      running total = {running}")
print("Program total:", total_running(week), "| hand-trace total: 917.50 ->", "MATCH" if total_running(week) == D("917.50") else "DIFFERENT")

print("\n=== Invalid entries are skipped, not added ===")
print(total_running(week + [(D("-1"), D("3.5"), D("8.5")), (D("5"), D("7.5"), D("8.5"))]), "(same 917.50)")

print("\n=== ALTERNATIVE: running total (O(1) space) vs stored list (O(n) space) ===")
base = [(D("10"), D("3.5"), D("8.5")), (D("8.5"), D("4.2"), D("8.7")), (D("12"), D("3.1"), D("8.3"))]
print(f"  {'n':>8} {'running ms':>11} {'stored ms':>10} {'running peak KB':>16} {'stored peak KB':>15}  equal?")
for n in (300, 6000, 150000):
    entries = [base[i % 3] for i in range(n)]
    t0 = time.perf_counter(); a = total_running(entries); t_a = (time.perf_counter() - t0) * 1000
    t0 = time.perf_counter(); b, _ = total_stored(entries); t_b = (time.perf_counter() - t0) * 1000
    tracemalloc.start(); total_running(entries); peak_a = tracemalloc.get_traced_memory()[1] / 1024; tracemalloc.stop()
    tracemalloc.start(); total_stored(entries); peak_b = tracemalloc.get_traced_memory()[1] / 1024; tracemalloc.stop()
    print(f"  {n:>8} {t_a:11.2f} {t_b:10.2f} {peak_a:16.1f} {peak_b:15.1f}  {a == b}")
print("""
Time is O(n) for both (each entry is handled once). Extra space: running total keeps ONE number
= O(1); the stored list keeps n amounts = O(n) (see the peak-memory columns growing).
Storing the entries is STILL necessary when you must: print a farmer's statement line by line,
audit or re-check any single payment, export every payment to the bank file, or re-calculate
after a rate correction - i.e. whenever the individual values are needed after the total.""")
