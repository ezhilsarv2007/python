"""Task 3 - Variables and named constants (K3 - Apply)."""
import rates
from rates import BASE_RATE, FAT_STEP_VALUE, SNF_STEP_VALUE, STANDARD_FAT, STANDARD_SNF, STEP_SIZE

print("=== 1. Naming rules ===")
print("Valid  : farmer_id, litres_1, _tmp, BASE_RATE      Invalid: 1litre, fat%, my rate, class")
import keyword
print("Reserved words cannot be names:", keyword.kwlist[:8], "...")
print("Convention: snake_case for variables/functions, UPPER_CASE for constants.\n")

print("=== 2. Constants live in rates.py ===")
print("BASE_RATE =", BASE_RATE, "| FAT_STEP_VALUE =", FAT_STEP_VALUE, "| SNF_STEP_VALUE =", SNF_STEP_VALUE)

print("\n=== 3. Python has no TRUE constants ===")
rates.BASE_RATE = 99.0       # Python allows this! Only convention (UPPER_CASE) protects it.
print("After rates.BASE_RATE = 99.0 ->", rates.BASE_RATE, "(the name was rebound, no error)")
rates.BASE_RATE = 30.00
print("Restored ->", rates.BASE_RATE, "(tools such as typing.Final / linters can warn, the interpreter does not stop you)")

print("\n=== 4. Dynamic typing: same name, different types ===")
x = 8
print("x =", x, type(x))
x = "eight"
print("x =", x, type(x))
x = 8.5
print("x =", x, type(x))
try:
    print(8 + "5")
except TypeError as err:
    print("8 + '5' ->", type(err).__name__, ":", err)
print("int('8') + 5 =", int("8") + 5, " | '8' + str(5) =", "8" + str(5))

print("\n=== 5. Multiple assignment and swapping ===")
fat, snf = 4.2, 8.7
print("fat, snf =", fat, snf)
fat, snf = snf, fat
print("after fat, snf = snf, fat ->", fat, snf)
low = high = 0
print("chained: low = high = 0 ->", low, high)
a, *rest = [10, 8.5, 4.2]
print("unpacking a, *rest ->", a, rest)

print("\n=== 6. ALTERNATIVES: magic numbers vs dictionary vs constants ===")
# (a) magic numbers - values typed in the expression
def rate_magic(fat, snf):
    return 30.00 + round((fat - 3.5) / 0.1) * 0.40 + round((snf - 8.5) / 0.1) * 0.30

# (b) dictionary RATE_CARD
RATE_CARD = {"base": 30.0, "fat": 0.40, "snf": 0.30}
def rate_dict(fat, snf):
    return RATE_CARD["base"] + round((fat - 3.5) / 0.1) * RATE_CARD["fat"] + round((snf - 8.5) / 0.1) * RATE_CARD["snf"]

# (c) named constants
def rate_const(fat, snf):
    return BASE_RATE + round((fat - STANDARD_FAT) / STEP_SIZE) * FAT_STEP_VALUE + round((snf - STANDARD_SNF) / STEP_SIZE) * SNF_STEP_VALUE

print("rate(4.2, 8.7): magic =", rate_magic(4.2, 8.7), "| dict =", rate_dict(4.2, 8.7), "| constants =", rate_const(4.2, 8.7))

import timeit
n = 300000
for name, fn in (("magic numbers", rate_magic), ("dict RATE_CARD", rate_dict), ("named constants", rate_const)):
    t = timeit.timeit(lambda: fn(4.2, 8.7), number=n)
    print(f"  {name:<16}: {t / n * 1e9:7.0f} ns per call")

print("""
Places to change for ONE rate revision (e.g. fat step 0.40 -> 0.45), k = number of
expressions that use it:
  magic numbers : k places (a missed one = a partly applied revision, the volunteer's bug)
  dictionary    : 1 place, but a typo in a key ("fta") only fails at run time (KeyError)
  named constants: 1 place, a typo in a name fails at once with NameError/linters
Running time: all O(1) per call; the dictionary lookup adds ~2 hash lookups (a few ns).
Memory: constants = a few objects, O(1) in all three designs.""")
