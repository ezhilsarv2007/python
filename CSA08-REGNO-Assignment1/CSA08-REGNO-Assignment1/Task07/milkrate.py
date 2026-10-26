"""Rate card of the village milk co-operative (used as a module)."""

BASE_RATE = 30.00       # Rs per litre for milk with 3.5 % fat and 8.5 % SNF

FAT_STEP_VALUE = 0.40   # Rs per litre for every 0.1 % of fat above or below 3.5

SNF_STEP_VALUE = 0.30   # Rs per litre for every 0.1 % of SNF above or below 8.5


def rate_per_litre(fat, snf):
    """Returns the price per litre, rounded to 2 decimals."""
    # TODO 1: Count the 0.1 % steps of fat from 3.5 and of SNF from 8.5 (round to the
    #  nearest whole step), add their values to BASE_RATE and round to 2 decimals
    fat_steps = round((fat - 3.5) / 0.1)
    snf_steps = round((snf - 8.5) / 0.1)
    return round(BASE_RATE + fat_steps * FAT_STEP_VALUE + snf_steps * SNF_STEP_VALUE, 2)


def payout(litres, fat, snf):
    """Returns the amount payable to the farmer, rounded to 2 decimals."""
    # TODO 2: Multiply litres by the rate per litre and round to 2 decimals
    return round(litres * rate_per_litre(fat, snf), 2)


if __name__ == "__main__":
    for litres, fat, snf in [(10, 3.5, 8.5), (8.5, 4.2, 8.7), (12, 3.1, 8.3)]:
        rate, pay = rate_per_litre(fat, snf), payout(litres, fat, snf)
        print(f"{litres:5} L  fat {fat}  snf {snf}  rate {rate:6.2f}  pay {pay:8.2f}")
