"""Task 2 - Alternative concept: integer paise, float+round() each addition, Decimal.
Measures time per addition, memory per value (sys.getsizeof) and exactness."""
import sys
import time
from decimal import Decimal

for n in (300, 6000, 150000):
    payments = ["33.40"] * n
    exact = Decimal("33.40") * n                      # known true bank total

    t0 = time.perf_counter()
    total_dec = Decimal("0")
    for p in payments:
        total_dec += Decimal(p)
    t_dec = time.perf_counter() - t0

    t0 = time.perf_counter()
    total_paise = 0
    for p in payments:
        rupees, _, paise = p.partition(".")          # exact text -> integer paise
        total_paise += int(rupees) * 100 + int((paise + "00")[:2])
    t_int = time.perf_counter() - t0

    t0 = time.perf_counter()
    total_round = 0.0
    for p in payments:
        total_round = round(total_round + float(p), 2)
    t_round = time.perf_counter() - t0

    t0 = time.perf_counter()
    total_float = 0.0
    for p in payments:
        total_float += float(p)
    t_float = time.perf_counter() - t0

    print(f"\nn = {n}   true total = {exact}")
    print(f"  {'method':<22}{'result':>22}{'exact?':>8}{'time/add (ns)':>16}")
    rows = [
        ("plain float", repr(total_float), total_float == float(exact), t_float),
        ("float + round() each", repr(total_round), total_round == float(exact), t_round),
        ("integer paise", f"{total_paise // 100}.{total_paise % 100:02d}", total_paise == int(exact * 100), t_int),
        ("Decimal", str(total_dec), total_dec == exact, t_dec),
    ]
    for name, res, ok, t in rows:
        print(f"  {name:<22}{res:>22}{str(ok):>8}{t / n * 1e9:16.0f}")

print("\nMemory per value (sys.getsizeof, bytes):")
for label, value in [("int paise 3340", 3340), ("float 33.4", 33.4), ("Decimal('33.40')", Decimal("33.40"))]:
    print(f"  {label:<20} {sys.getsizeof(value)}")

print("""
Analysis
  - Time per addition is O(1) for every method; total time is O(n).
  - int paise uses the least memory (28 bytes against 104 for Decimal) and is exact,
    but here the text had to be split into rupees and paise first, so it is not
    faster than Decimal; every multiplication (litres x rate) also needs manual care.
    (Timings change a little on every run; the ORDER of growth is what matters.)
  - float + round() each step hides drift but is NOT guaranteed exact for large n
    (round(x, 2) on a binary float is still a float).
  - Decimal is slightly slower and bigger but exact, readable, and has built-in
    rounding modes, so it is the safest for money.""")
