"""Task 2 - Explore values and types, reproduced as an annotated >>> session."""
from decimal import Decimal
import math

LINES = [
    ("# --- types ---", None),
    ("type(10)", None),
    ("type(10.0)", None),
    ('type("10")', None),
    ("type(True)", None),
    ("type([10, 8.5])", None),
    ("isinstance(True, int)", None),
    ("True + True", None),
    ("# --- division operators ---", None),
    ("7 / 2", None),
    ("7 // 2", None),
    ("7 % 2", None),
    ("-7 // 2", None),
    ("-7 % 2", None),
    ("# --- floating point ---", None),
    ("0.1 + 0.2", None),
    ("0.1 + 0.2 == 0.3", None),
    ("Decimal('0.1') + Decimal('0.2')", None),
    ("Decimal('0.1') + Decimal('0.2') == Decimal('0.3')", None),
    ("Decimal(0.1)", None),
    ("round(2.675, 2)", None),
    ("math.isclose(0.1 + 0.2, 0.3)", None),
    ("# --- money ---", None),
    ("sum([0.1] * 10)", None),
    ("sum([0.1] * 10) == 1.0", None),
    ("33.40 * 1000", None),
    ("int(33.40 * 100)", None),
    ("round(33.40 * 100)", None),
]

print("Python interactive session (reproduced; every line was evaluated by Python)\n")
for line, _ in LINES:
    if line.startswith("#"):
        print(line)
        continue
    print(">>>", line)
    print(repr(eval(line)))

print("""
EXPLANATIONS
  type(...)            : 10 is int, 10.0 is float, "10" is str (quotes make it text),
                         True is bool, [10, 8.5] is list.
  isinstance(True,int) : bool is a SUBCLASS of int, so True + True == 2.
  7 / 2 = 3.5          : / is true division and always returns a float.
  7 // 2 = 3           : // is floor division (largest integer <= result).
  7 % 2 = 1            : % is the remainder; a // b * b + a % b == a always holds.
  -7 // 2 = -4         : floor of -3.5 is -4 (towards minus infinity), NOT -3.
  -7 % 2 = 1           : to satisfy (-4)*2 + 1 == -7.
  0.1 + 0.2 == 0.3     : False. 0.1, 0.2 and 0.3 cannot be stored exactly in binary,
                         so the sum is 0.30000000000000004, not 0.3.
  Decimal('0.1') ...   : Decimal stores decimal digits exactly, so the test is True.
  Decimal(0.1)         : shows the TRUE binary value stored for the float 0.1.
  round(2.675, 2)=2.67 : 2.675 is really 2.67499999..., so it rounds down.
  int(33.40*100)=3339  : 33.40*100 = 3339.9999999999995 and int() TRUNCATES: a paisa lost!
""")
