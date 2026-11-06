from pathlib import Path
def read_attendance(file_name):
    records = []
    with open(file_name, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split(",")
            if len(parts) == 3 and parts[2] in ("P", "A"):
                records.append(parts)
    return records

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

def write_report(percentages, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        for register_number, percentage in sorted(percentages.items()):
            file.write(f"{register_number}: {percentage:.2f}%\n")

def main():
    folder = Path(__file__).parent
    records = read_attendance(folder / "input.txt")
    percentages = calculate_percentages(records)
    write_report(percentages, folder / "output" / "report.txt")
    print(percentages)

if __name__ == "__main__":
    main()
