"""Second script: imports milkrate and calls payout() (Task 7)."""
import sys
import time

print("=== 1. Three ways to import ===")
import milkrate
print("import milkrate            ->", milkrate.payout(8.5, 4.2, 8.7), "(call with the module name: milkrate.payout)")
from milkrate import payout
print("from milkrate import payout ->", payout(12, 3.1, 8.3), "(name used directly; other names not imported)")
import milkrate as mr
print("import milkrate as mr      ->", mr.rate_per_litre(4.2, 8.7), "(short alias; same module object:", mr is milkrate, ")")

print("\n=== 2. Why the table did NOT print on import ===")
print("milkrate.__name__ =", milkrate.__name__, "(the module's own name when imported)")
print("this script's __name__ =", __name__, "(only the file run directly is '__main__')")
print("So the block 'if __name__ == \"__main__\":' inside milkrate.py was skipped.")

print("\n=== 3. WITHOUT the guard (milkrate_noguard.py) ===")
import milkrate_noguard
print("Imported milkrate_noguard; its demo table printed above by itself - unwanted side effect.")

print("\n=== 4. Standard modules ===")
import math
from decimal import Decimal
print("math.floor(-2.5) =", math.floor(-2.5), "| math.sqrt(16) =", math.sqrt(16), "| Decimal('0.1')*3 =", Decimal("0.1") * 3)

print("\n=== 5. Where Python looks for modules ===")
print("sys.path[0] (folder of the running script):", sys.path[0] or "(current folder)")
print("first 4 entries of sys.path:")
for p in sys.path[:4]:
    print("  ", p)
print("milkrate was loaded from:", milkrate.__file__)

print("\n=== 6. Import cost: loaded once, kept in sys.modules ===")
print("'milkrate' in sys.modules ->", "milkrate" in sys.modules)
t0 = time.perf_counter()
import milkrate as again
t_again = time.perf_counter() - t0
print(f"importing it AGAIN took {t_again * 1e6:.1f} microseconds; same object: {again is milkrate}")
