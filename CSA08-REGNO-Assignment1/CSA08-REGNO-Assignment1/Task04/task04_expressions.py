"""Task 4 - Write correct expressions (K4 - Analyse)."""
import math

BASE_RATE, FAT_STEP_VALUE, SNF_STEP_VALUE = 30.00, 0.40, 0.30

def fat_steps(fat):
    return round((fat - 3.5) / 0.1)

def snf_steps(snf):
    return round((snf - 8.5) / 0.1)

def rate_per_litre(fat, snf):
    return round(BASE_RATE + fat_steps(fat) * FAT_STEP_VALUE + snf_steps(snf) * SNF_STEP_VALUE, 2)

def amount(litres, fat, snf):
    return round(litres * rate_per_litre(fat, snf), 2)

print("=== The required expressions ===")
print("fat_steps(4.2)          =", fat_steps(4.2))
print("snf_steps(8.7)          =", snf_steps(8.7))
print("rate_per_litre(4.2,8.7) =", rate_per_litre(4.2, 8.7))
print("amount(8.5,4.2,8.7)     =", amount(8.5, 4.2, 8.7))

print("\n=== Operator precedence and associativity ===")
for e in ["2 + 3 * 4", "(2 + 3) * 4", "2 ** 3 ** 2", "(2 ** 3) ** 2", "-2 ** 2", "(-2) ** 2",
          "10 - 4 - 3", "100 / 10 / 5", "-7 // 2", "not True or True", "not (True or True)"]:
    print(f"  {e:<22} -> {eval(e)}")
print("  ** is RIGHT associative and binds tighter than unary minus; - and / are LEFT associative.")

print("\n=== Surprises ===")
print("1) (4.2 - 3.5) / 0.1 =", (4.2 - 3.5) / 0.1, "  <- not exactly 7")
print("   int((4.2 - 3.5) / 0.1) =", int((4.2 - 3.5) / 0.1), "| round(...) =", round((4.2 - 3.5) / 0.1))
print("2) (3.1 - 3.5) / 0.1 =", (3.1 - 3.5) / 0.1, "  int() gives", int((3.1 - 3.5) / 0.1),
      "(WRONG, should be -4); round() gives", round((3.1 - 3.5) / 0.1))
print("3) round(2.5) =", round(2.5), "| round(3.5) =", round(3.5), "| round(0.5) =", round(0.5),
      " <- banker's rounding (ties go to the EVEN number)")
print("4) round(2.675, 2) =", round(2.675, 2), " <- 2.675 is stored as 2.67499999...")
print("5) 0.1 + 0.2 =", 0.1 + 0.2)
print("6) -2 ** 2 =", -2 ** 2, " <- power first, then minus")

print("\n=== round() vs int() vs math.floor() for negative values ===")
print(f"  {'x':>6} {'round':>6} {'int':>5} {'floor':>6} {'ceil':>5}")
for x in (-2.5, -2.4, -2.6, 2.5, 2.6):
    print(f"  {x:6} {round(x):6} {int(x):5} {math.floor(x):6} {math.ceil(x):5}")
print("  int() truncates towards 0, floor() goes down, round() goes to nearest (ties to even).")

print("\n=== Comparison chaining and Boolean operators ===")
fat = 4.2
print("2.0 <= fat <= 7.0 with fat=4.2 ->", 2.0 <= fat <= 7.0)
for fat in (1.9, 2.0, 7.0, 7.1):
    print(f"  fat={fat}: 2.0 <= fat <= 7.0 -> {2.0 <= fat <= 7.0}   (same as 2.0 <= fat and fat <= 7.0)")
litres, fat, snf = 10, 4.2, 8.5
print("valid? ->", litres > 0 and 2.0 <= fat <= 7.0 and 7.0 <= snf <= 10.0, "(and stops at first False: short-circuit)")

print("\n=== ALTERNATIVE: int() / math.floor() instead of round() ===")
def rate_with(step_fn, fat, snf):
    return round(BASE_RATE + step_fn((fat - 3.5) / 0.1) * FAT_STEP_VALUE + step_fn((snf - 8.5) / 0.1) * SNF_STEP_VALUE, 2)

print(f"  {'fat':>4} {'snf':>4} | {'round':>7} {'int':>7} {'floor':>7}")
for fat, snf in [(4.2, 8.5), (3.1, 8.5), (4.2, 8.7), (3.1, 8.3)]:
    print(f"  {fat:4} {snf:4} | {rate_with(round, fat, snf):7.2f} {rate_with(int, fat, snf):7.2f} {rate_with(math.floor, fat, snf):7.2f}")
print("""  Correct answers: fat 4.2 -> 32.80 ; fat 3.1 -> 28.40 ; (4.2, 8.7) -> 33.40.
  int() truncates TOWARDS ZERO: (3.1-3.5)/0.1 = -3.999999 -> -3 instead of -4, so the rate
  for fat 3.1 is 28.80 (a farmer is OVERPAID Rs 0.40 per litre).
  floor() goes DOWN: (8.7-8.5)/0.1 = 1.999999 -> 1 instead of 2, so (4.2, 8.7) gives 33.10
  (a farmer is UNDERPAID Rs 0.30 per litre).
  Only round() is safe, because it moves to the NEAREST whole step, so a tiny float error
  of 1e-15 can never change the step count.
  Cost: each is one arithmetic expression plus one call: time O(1), space O(1).""")
