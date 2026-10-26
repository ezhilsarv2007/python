"""Task 5 - Read input and convert types (K3 - Apply).
Run:  python task05_input.py          (demo with prepared inputs)
      python task05_input.py --live   (really type the values with input())"""
import sys
import timeit


def is_valid_number(text):
    """Method 1: check with str methods BEFORE converting."""
    t = text.strip()
    if t[:1] in "+-":
        t = t[1:]
    if t == "" or t.count(".") > 1:
        return False
    return t.replace(".", "", 1).isdigit()


def to_float_checked(text):
    """Returns float or None using the str-method check."""
    return float(text.strip()) if is_valid_number(text) else None


def to_float_try(text):
    """Method 2 (alternative): EAFP - just try, catch ValueError."""
    try:
        return float(text)
    except ValueError:
        return None


def rate(fat, snf):
    return round(30.00 + round((fat - 3.5) / 0.1) * 0.40 + round((snf - 8.5) / 0.1) * 0.30, 2)


if "--live" in sys.argv:
    print("input() always returns a STRING:")
    litres_text = input("Litres  : ")
    fat_text = input("Fat %   : ")
    snf_text = input("SNF %   : ")
    litres, fat, snf = (to_float_checked(t) for t in (litres_text, fat_text, snf_text))
    if None in (litres, fat, snf):
        print("Invalid number entered - please retype.")
    else:
        print(f"{litres:8.1f} L {fat:5.1f} {snf:5.1f}  rate {rate(fat, snf):7.2f}  amount {litres * rate(fat, snf):10.2f}")
    sys.exit()

print("=== 1. input() returns str; conversion with int() / float() ===")
typed = "8.5"
print(repr(typed), type(typed), "->", float(typed), type(float(typed)))
print("int('12') =", int("12"), "| float('12') =", float("12"))
for bad in ("8.5", "12.0"):
    try:
        print(f"int({bad!r}) =", int(bad))
    except ValueError as e:
        print(f"int({bad!r}) -> ValueError: {e}")
print("'8.5' * 2 =", "8.5" * 2, "(string repetition, not 17.0!)")

print("\n=== 2. Clerk typing mistakes: str-method check vs try/except ===")
tests = ["8.5", " 8.5 ", "8,5", "eight", "", "-3", "8.5.1", "1e2", "nan", "inf", "1_0", ".5"]
print(f"  {'text':<10} {'isdigit-check':>14} {'try/except':>12}")
for t in tests:
    print(f"  {t!r:<10} {str(to_float_checked(t)):>14} {str(to_float_try(t)):>12}")
print("""  Notes:
  - "8,5" and "eight" are rejected by BOTH (ValueError / failed check).
  - " 8.5 " is accepted by both (spaces are stripped by float()).
  - float() ALSO accepts 'nan', 'inf', '1e2', '1_0': try/except alone lets these through,
    so the str-method check is stricter; after try/except you must add a range test.""")

print("\n=== 3. Time per entry (timeit, 200,000 calls each) ===")
for label, text in (("valid '8.5'", "8.5"), ("invalid 'eight'", "eight"), ("invalid '8,5'", "8,5")):
    t1 = timeit.timeit(lambda: to_float_checked(text), number=200000) / 200000 * 1e9
    t2 = timeit.timeit(lambda: to_float_try(text), number=200000) / 200000 * 1e9
    print(f"  {label:<16} str-check {t1:7.0f} ns | try/except {t2:7.0f} ns")
print("  Both are O(1) per entry (O(len(text)) for the characters, tiny). Raising an exception is")
print("  slower than a plain check when input is usually INVALID, faster-or-equal when usually valid.")

print("\n=== 4. Aligned output with f-strings (width and precision) ===")
entries = [("F001", 10, 3.5, 8.5), ("F002", 8.5, 4.2, 8.7), ("F003", 12, 3.1, 8.3), ("F104", 120.25, 5.0, 9.0)]
print(f"{'Farmer':<8}{'Litres':>9}{'Fat':>6}{'SNF':>6}{'Rate':>9}{'Amount':>11}")
print("-" * 49)
for fid, litres, fat, snf in entries:
    r = rate(fat, snf)
    amount = round(litres * r, 2)
    print(f"{fid:<8}{litres:9.2f}{fat:6.1f}{snf:6.1f}{r:9.2f}{amount:11.2f}")
print("{amount:8.2f} -> width 8, 2 decimals, right aligned; {name:<8} left aligned; {x:,.2f} adds commas:",
      f"{1234567.891:,.2f}")
