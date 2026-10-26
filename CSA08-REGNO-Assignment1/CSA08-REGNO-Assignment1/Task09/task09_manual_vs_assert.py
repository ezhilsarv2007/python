"""Task 9 - Alternative concept: testing by hand versus an assert-based test function."""
import subprocess
import sys
import time

SECONDS_PER_MANUAL_TEST = 15       # assumption: type 5 values + read + compare with a hand calculation
TESTS = 26

t0 = time.perf_counter()
result = subprocess.run([sys.executable, "test_milk_calculator.py"], capture_output=True, text=True)
elapsed = time.perf_counter() - t0

print(f"Automated: all {TESTS} tests re-run in {elapsed:.2f} s (including starting Python); exit code {result.returncode}")
print(f"Manual   : {TESTS} tests x {SECONDS_PER_MANUAL_TEST} s of typing and checking = {TESTS * SECONDS_PER_MANUAL_TEST / 60:.1f} minutes")
print("""
Re-running after EVERY change (say 20 changes in a day):
  manual    : 20 x 6.5 min = 130 min of human time, and tired people skip cases, mistype or
              forget the expected value -> bugs slip through. Time grows O(t) per change in HUMAN time.
  assert    : 20 x ~0.2 s = 4 s, identical every time, a failing assert pinpoints the broken case.
              Also O(t) in the number of tests, but with a tiny constant (milliseconds per test).
Conclusion: write each new bug or requirement as a test once; the computer repeats it for free.""")
