"""Alternative concept: copying the rate functions into every script (Task 7)."""
import importlib
import time

SCRIPTS = 5     # imagine 5 different scripts (payment, report, bank file, SMS, audit)
print("If the rate function is COPIED into", SCRIPTS, "scripts, a rate revision means editing",
      SCRIPTS, "files (k places); with a module it means editing 1 file.")
print("Forget one copy and farmers are paid by two different rate cards.\n")

t0 = time.perf_counter()
import milkrate
t_first = time.perf_counter() - t0
t0 = time.perf_counter()
for _ in range(1000):
    importlib.import_module("milkrate")          # repeated imports hit sys.modules
t_rep = (time.perf_counter() - t0) / 1000
print(f"first import of milkrate: {t_first * 1e6:8.1f} microseconds (find file + compile/read + run once)")
print(f"each later import       : {t_rep * 1e6:8.2f} microseconds (dictionary lookup in sys.modules)")
print("One-time cost O(size of module); every later import O(1). Copying costs O(k) maintenance forever.")
