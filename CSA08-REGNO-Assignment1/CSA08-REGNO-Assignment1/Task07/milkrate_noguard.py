"""Same module but WITHOUT the if __name__ == '__main__' guard (for the demonstration)."""
BASE_RATE = 30.00
FAT_STEP_VALUE = 0.40
SNF_STEP_VALUE = 0.30


def rate_per_litre(fat, snf):
    """Returns the price per litre, rounded to 2 decimals."""
    return round(BASE_RATE + round((fat - 3.5) / 0.1) * FAT_STEP_VALUE + round((snf - 8.5) / 0.1) * SNF_STEP_VALUE, 2)


def payout(litres, fat, snf):
    """Returns the amount payable to the farmer, rounded to 2 decimals."""
    return round(litres * rate_per_litre(fat, snf), 2)


print("   >>> this table is printed at IMPORT time because there is no guard <<<")
for litres, fat, snf in [(10, 3.5, 8.5), (8.5, 4.2, 8.7), (12, 3.1, 8.3)]:
    print(f"{litres:5} L  fat {fat}  snf {snf}  rate {rate_per_litre(fat, snf):6.2f}  pay {payout(litres, fat, snf):8.2f}")
