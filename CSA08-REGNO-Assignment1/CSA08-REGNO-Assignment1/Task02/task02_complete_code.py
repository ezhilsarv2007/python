"""Task 2 - Complete the Code (TODO 1 completed) and the Decimal(float()) experiment."""
from decimal import Decimal

# 1,000 payments of Rs 33.40 and three small adjustments of Rs 0.10
payments = ["33.40"] * 1000 + ["0.10"] * 3


def total_float(items):
    total = 0.0
    for amount in items:
        total += float(amount)
    return total


def total_decimal(items):
    # TODO 1: Add the amounts exactly by creating a Decimal from each string, and
    #  return the Decimal total
    total = Decimal("0")
    for amount in items:
        total += Decimal(amount)
    return total


print("float  :", total_float(payments))
print("Decimal:", total_decimal(payments))
print(0.1 + 0.2 == 0.3, Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))

# ---- experiment asked in the task: Decimal(amount) -> Decimal(float(amount))
def total_decimal_from_float(items):
    total = Decimal("0")
    for amount in items:
        total += Decimal(float(amount))
    return total


print("\nExperiment: Decimal(float(amount))")
print("Decimal(float(...)):", total_decimal_from_float(payments))
print("Decimal(float('33.40')) =", Decimal(float("33.40")))
print("""
Explanation: float('33.40') is ALREADY the binary approximation
33.39999999999999857891452847979962825775146484375. Decimal(float) copies that
wrong value exactly, so the error is carried into the Decimal total. A Decimal
must be created from the STRING '33.40' (or an int), never from a float.""")
