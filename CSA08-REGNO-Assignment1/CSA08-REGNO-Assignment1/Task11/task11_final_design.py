"""Task 11 - Recommend and defend the final design (K5 - Evaluate).
Evidence for the recommendation: exactness, scale, rate revision from a JSON file, start-up cost."""
import json
import os
import random
import sys
import tempfile
import time
from decimal import Decimal as D

import milk_calculator as mc

print("=== EVIDENCE 1: exact money at district-union scale (150,000 farmers) ===")
rnd = random.Random(7)
n = 150000
entries = [(D(f"{rnd.randint(20, 400) / 10:.1f}"), D(f"{rnd.randint(20, 70) / 10:.1f}"), D(f"{rnd.randint(78, 95) / 10:.1f}"))
           for _ in range(n)]
t0 = time.perf_counter()
total = sum((mc.payout(l, f, s) for l, f, s in entries), D("0"))
elapsed = time.perf_counter() - t0
print(f"{n} payments -> total Rs {total} in {elapsed:.2f} s  (every payment correct to the paisa)")
print("Two decimal places guaranteed:", total == total.quantize(D("0.01")))

print("\n=== EVIDENCE 2: rate card read from a JSON file at start-up ===")


def load_rate_card(path):
    """Read the rate card (strings) and return a dict of Decimals."""
    with open(path) as f:
        raw = json.load(f)
    return {name: D(value) for name, value in raw.items()}


def rate_with(card, fat, snf):
    """Rate per litre computed from a loaded rate card instead of module constants."""
    fat_steps = ((fat - card["standard_fat"]) / card["step"]).to_integral_value(rounding="ROUND_HALF_UP")
    snf_steps = ((snf - card["standard_snf"]) / card["step"]).to_integral_value(rounding="ROUND_HALF_UP")
    return mc.money(card["base_rate"] + fat_steps * card["fat_step_value"] + snf_steps * card["snf_step_value"])


here = os.path.dirname(os.path.abspath(__file__))
card = load_rate_card(os.path.join(here, "rate_card.json"))
print("Loaded:", {k: str(v) for k, v in card.items()})
print("rate(4.2, 8.7) with the JSON card :", rate_with(card, D("4.2"), D("8.7")), "(must equal module result", mc.rate_per_litre(D("4.2"), D("8.7")), ")")

print("\nRate revision WITHOUT touching the program: edit only the JSON text")
revised = dict(json.load(open(os.path.join(here, "rate_card.json"))))
revised["base_rate"], revised["fat_step_value"] = "32.00", "0.45"
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
    json.dump(revised, tmp)
new_card = load_rate_card(tmp.name)
os.unlink(tmp.name)
print("rate(4.2, 8.7) with revised card  :", rate_with(new_card, D("4.2"), D("8.7")), "(32.00 + 7 x 0.45 + 2 x 0.30 = 35.75)")

print("\n=== EVIDENCE 3: start-up time and space for t values in the file ===")
print(f"{'t values':>10} {'file bytes':>11} {'read+convert (ms)':>18} {'dict bytes':>11}")
for t in (6, 600, 60000):
    data = {f"value_{i}": f"{i}.00" for i in range(t)}
    text = json.dumps(data)
    t0 = time.perf_counter()
    loaded = {k: D(v) for k, v in json.loads(text).items()}
    ms = (time.perf_counter() - t0) * 1000
    print(f"{t:>10} {len(text):>11} {ms:18.3f} {sys.getsizeof(loaded):>11}")
print("A rate card has about 6-10 values: reading it costs microseconds, O(t) time and O(t) space, once per run.")

print("""
=== RECOMMENDATION (based on the experiments above and in Tasks 2, 4 and 10) ===
Types      : Decimal for litres, fat, snf, rates and money (never float); str for ids and shift;
             int only for counts.
Rounding   : ROUND_HALF_UP to the paisa on EACH payment; ten-day total = sum of rounded payments;
             steps counted with round-to-nearest (never int() or floor()).
Revision   : change the rate values in ONE place - rate_card.json (strings, so Decimal is exact) -
             with no program change; keep a dated copy of each card for audit.
Structure  : constants/rate card in one module, small functions (rate, payout, validate),
             assert-based tests re-run after every change.
Limitations: Decimal is ~5-8x slower than float (still < 1 s for 150,000 payments);
             SNF limits and the 1000 L cap are assumptions to be confirmed with the union;
             a JSON card has no validation of its own - a typo in a value is read as is
             (should check ranges after loading); entries are processed in memory, so a
             district union running millions of rows would need streaming or a database;
             one rate card applies to all dates (seasons are handled in Task 12).
Scale      : correct at 300, 6,000 and 150,000 farmers: time grows linearly, O(n), and the
             running total needs O(1) extra memory.""")
