"""Task 6 - Organise the logic into functions (K3 - Apply)."""
import random
import time

BASE_RATE = 30.00
FAT_STEP_VALUE = 0.40
SNF_STEP_VALUE = 0.30


def rate_per_litre(fat, snf):
    """Return the price per litre (float, 2 decimals) for the given fat % and SNF %.

    Parameters: fat (float), snf (float). Reads the module constants; changes none.
    """
    fat_steps = round((fat - 3.5) / 0.1)
    snf_steps = round((snf - 8.5) / 0.1)
    return round(BASE_RATE + fat_steps * FAT_STEP_VALUE + snf_steps * SNF_STEP_VALUE, 2)


def payout(litres, fat, snf):
    """Return the amount payable (litres x rate), rounded to 2 decimals."""
    return round(litres * rate_per_litre(fat, snf), 2)


def ten_day_total(entries):
    """Return the sum of the payouts of (litres, fat, snf) tuples, rounded to 2 decimals."""
    total = 0.0
    for litres, fat, snf in entries:
        total += payout(litres, fat, snf)
    return round(total, 2)


def show_payout(litres, fat, snf):
    """PRINTS the payout and returns None - useless for further calculation."""
    print("payout is", payout(litres, fat, snf))


if __name__ == "__main__":
    print("=== functions, parameters, return values ===")
    print("rate_per_litre(4.2, 8.7) =", rate_per_litre(4.2, 8.7))
    print("payout(8.5, 4.2, 8.7)    =", payout(8.5, 4.2, 8.7))
    week = [(10, 3.5, 8.5), (8.5, 4.2, 8.7), (12, 3.1, 8.3)]
    print("ten_day_total(week)      =", ten_day_total(week))

    print("\n=== return vs print ===")
    result = show_payout(10, 3.5, 8.5)
    print("value kept from show_payout:", result, "(None - it only printed)")
    total = payout(10, 3.5, 8.5) + payout(8.5, 4.2, 8.7)
    print("value returned by payout() can be reused:", total)

    print("\n=== docstrings ===")
    for fn in (rate_per_litre, payout, ten_day_total):
        print(f"{fn.__name__}: {fn.__doc__.splitlines()[0]}")
    print("help() reads the same text:", payout.__doc__ is not None)

    print("\n=== local vs global names ===")
    def read_constant():
        return BASE_RATE            # READING a global is fine
    def try_to_change():
        try:
            BASE_RATE = BASE_RATE + 1   # assignment makes BASE_RATE LOCAL for the whole function
        except UnboundLocalError as e:
            return f"UnboundLocalError: {e}"
    def local_only():
        BASE_RATE = 99.0                # creates a separate LOCAL variable, global unchanged
        return BASE_RATE
    print("read_constant()  ->", read_constant())
    print("try_to_change()  ->", try_to_change())
    print("local_only()     ->", local_only(), "| global BASE_RATE still", BASE_RATE)
    print("Rule: functions may READ constants; never rebind them (no 'global BASE_RATE' for rates).")

    print("\n=== ALTERNATIVE: one long script / lambda vs functions (timing) ===")
    random.seed(1)
    rate_lambda = lambda fat, snf: round(30.00 + round((fat - 3.5) / 0.1) * 0.40 + round((snf - 8.5) / 0.1) * 0.30, 2)
    print(f"  {'n':>8} {'functions (ms)':>15} {'inline script (ms)':>19} {'lambda (ms)':>12}  same total?")
    for n in (300, 6000, 150000):
        data = [(round(random.uniform(2, 40), 1), random.randint(20, 70) / 10, random.randint(78, 95) / 10) for _ in range(n)]
        t0 = time.perf_counter(); a = ten_day_total(data); t_f = (time.perf_counter() - t0) * 1000
        t0 = time.perf_counter()
        b = 0.0
        for litres, fat, snf in data:     # everything written out inline, no function calls
            b += round(litres * round(30.00 + round((fat - 3.5) / 0.1) * 0.40 + round((snf - 8.5) / 0.1) * 0.30, 2), 2)
        b = round(b, 2); t_s = (time.perf_counter() - t0) * 1000
        t0 = time.perf_counter()
        c = 0.0
        for litres, fat, snf in data:
            c += round(litres * rate_lambda(fat, snf), 2)
        c = round(c, 2); t_l = (time.perf_counter() - t0) * 1000
        print(f"  {n:>8} {t_f:15.2f} {t_s:19.2f} {t_l:12.2f}  {a == b == c}")
    print("""  All are O(n) time, O(1) extra space. The measured difference between functions, inline
  code and lambda is within normal timing noise (a call costs well under a microsecond and
  the arithmetic dominates), so function-call overhead is NOT a reason to avoid functions.
  Functions give: no repeated code, one place to
  fix a bug, docstrings, and easy testing. A lambda is just an unnamed one-expression function:
  no docstring, no statements, harder to debug.""")
