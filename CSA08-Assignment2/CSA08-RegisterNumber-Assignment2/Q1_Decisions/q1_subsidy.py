"""Q1: Electricity subsidy eligibility."""


def separate_if_decision(units, ration_card, senior_member):
    """Show why independent if statements can produce overlapping results."""
    results = []
    if units <= 100:
        results.append("Full subsidy")
    if 101 <= units <= 200 and ration_card:
        results.append("Partial subsidy")
    if units > 200 and senior_member:
        results.append("Senior-member exception subsidy")
    if not results:
        results.append("No subsidy")
    return results


def elif_decision(units, ration_card, senior_member):
    """Return exactly one decision for a household."""
    if units <= 100:
        return "Full subsidy"
    elif 101 <= units <= 200 and ration_card:
        return "Partial subsidy"
    elif units > 200 and senior_member:
        return "Senior-member exception subsidy"
    else:
        return "No subsidy"


households = [
    ("H1", 100, False, False),
    ("H2", 101, True, False),
    ("H3", 150, False, False),
    ("H4", 200, True, False),
    ("H5", 201, False, False),
    ("H6", 250, False, True),
    ("H7", 80, True, True),
    ("H8", 200, True, True),
]

print("HOUSEHOLD SUBSIDY CHECK")
print("-" * 78)
for name, units, ration, senior in households:
    old_result = separate_if_decision(units, ration, senior)
    new_result = elif_decision(units, ration, senior)
    print(name, "| units:", units, "| ration:", ration, "| age 80+:", senior)
    print("  Separate if :", ", ".join(old_result))
    print("  if-elif-else:", new_result)

print("\nDesign decision: if-elif-else is clearer because the household receives one decision.")
