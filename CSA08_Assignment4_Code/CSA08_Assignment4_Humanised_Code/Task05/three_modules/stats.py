def calculate_percentages(records):
    totals = {}
    for register_number, date, status in records:
        totals.setdefault(register_number, {"P": 0, "A": 0})
        totals[register_number][status] += 1

    percentages = {}
    for register_number, counts in totals.items():
        total_days = counts["P"] + counts["A"]
        percentages[register_number] = counts["P"] / total_days * 100
    return percentages
