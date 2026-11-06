from pathlib import Path

BASE_FOLDER = Path(__file__).parent


def process_month(folder):
    attendance = {}
    damaged_lines = []

    for file_path in sorted(folder.glob("*.txt")):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(",")
                    if len(parts) != 3:
                        damaged_lines.append(
                            f"{file_path.name}, line {line_number}: {line}"
                        )
                        continue

                    register_number, date, status = parts
                    if status not in ("P", "A"):
                        damaged_lines.append(
                            f"{file_path.name}, line {line_number}: invalid status {status}"
                        )
                        continue

                    attendance.setdefault(register_number, {"P": 0, "A": 0})
                    attendance[register_number][status] += 1
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as error:
            damaged_lines.append(f"{file_path.name}: {type(error).__name__}: {error}")

    report = ["Register Number,Present,Absent,Percentage"]
    below_75 = ["Register Number,Attendance Percentage"]

    for register_number, counts in sorted(attendance.items()):
        total_days = counts["P"] + counts["A"]
        percentage = counts["P"] / total_days * 100 if total_days else 0
        report.append(
            f"{register_number},{counts['P']},{counts['A']},{percentage:.2f}"
        )
        if percentage < 75:
            below_75.append(f"{register_number},{percentage:.2f}")

    return report, below_75, damaged_lines


def main():
    output_folder = BASE_FOLDER / "output"
    output_folder.mkdir(exist_ok=True)
    report, below_75, damaged = process_month(BASE_FOLDER / "input")

    files_to_write = {
        "monthly_attendance.csv": report,
        "below_75_percent.csv": below_75,
        "damaged_lines.log": damaged or ["No damaged lines."]
    }
    for file_name, lines in files_to_write.items():
        with open(output_folder / file_name, "w", encoding="utf-8") as file:
            file.write("\n".join(lines) + "\n")

    print("\n".join(report))
    print("Students below 75%:", len(below_75) - 1)
    print("Damaged lines:", len(damaged))


if __name__ == "__main__":
    main()
