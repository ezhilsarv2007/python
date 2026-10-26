"""Revised design (Task 12): seasonal rate cards, two-decimal analyser readings, ten-day bonus.

Decision: MODIFY the original design (keep: constants-in-one-place, small functions, Decimal,
round each payment). Change: the rate becomes a RateCard chosen by date, steps may be
fractional (analyser gives 2 decimals), and the bonus is a separate ten-day function.
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal as D, ROUND_HALF_UP

PAISA = D("0.01")
STANDARD_FAT, STANDARD_SNF, STEP = D("3.5"), D("8.5"), D("0.1")


@dataclass(frozen=True)
class RateCard:
    """All rates of one season, so a revision is one new object, not edits in many functions."""
    name: str
    base_rate: D
    fat_step_value: D
    snf_step_value: D


NORMAL = RateCard("normal (Jul-Mar)", D("30.00"), D("0.40"), D("0.30"))
SUMMER = RateCard("summer (Apr-Jun)", D("32.00"), D("0.45"), D("0.30"))
SUMMER_MONTHS = (4, 5, 6)

BONUS_THRESHOLD_LITRES = D("500")    # bonus only for MORE than 500 L in ten days
BONUS_PER_LITRE = D("0.50")          # assumption: paid on ALL litres of the ten days


def money(value):
    """Round to the paisa, halves up."""
    return value.quantize(PAISA, rounding=ROUND_HALF_UP)


def select_rate_card(on_date):
    """Return the RateCard valid on the given datetime.date."""
    return SUMMER if on_date.month in SUMMER_MONTHS else NORMAL


def steps(value, standard):
    """Exact (possibly fractional) number of 0.1 % steps from the standard, e.g. 4.25 -> 7.5."""
    return (value - standard) / STEP


def rate_per_litre(fat, snf, card):
    """Rate in Rs/litre for Decimal fat and snf under the given card; fractional steps are pro-rated."""
    rate = card.base_rate + steps(fat, STANDARD_FAT) * card.fat_step_value \
        + steps(snf, STANDARD_SNF) * card.snf_step_value
    return money(rate)


def payout(litres, fat, snf, on_date):
    """Amount payable for one entry on a date (rate card chosen from the date)."""
    return money(litres * rate_per_litre(fat, snf, select_rate_card(on_date)))


def bonus(total_litres):
    """Ten-day bonus: Rs 0.50 per litre if total litres > 500, else 0.00."""
    if total_litres > BONUS_THRESHOLD_LITRES:
        return money(total_litres * BONUS_PER_LITRE)
    return D("0.00")


def ten_day_statement(entries):
    """entries: list of (date, litres, fat, snf). Returns (litres, payments, bonus, grand_total)."""
    total_litres = sum((e[1] for e in entries), D("0"))
    payments = sum((payout(l, f, s, d) for d, l, f, s in entries), D("0"))
    b = bonus(total_litres)
    return total_litres, payments, b, payments + b
