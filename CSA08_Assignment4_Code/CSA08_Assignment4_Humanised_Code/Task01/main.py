from pathlib import Path

BASE_FOLDER = Path(__file__).parent


def prepare_mess_report(file_name):
    total_amount = 0.0
    report_lines = []
    rejected_lines = []

    try:
        with open(file_name, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if not line:
                    continue

                parts = line.split(",")
                try:
                    if len(parts) != 3:
                        raise ValueError("Expected register number, name and amount")
                    register_number, student_name, amount_text = parts
                    amount = float(amount_text)
                    report_lines.append(
                        f"{register_number} - {student_name}: Rs. {amount:.2f}"
                    )
                    total_amount += amount
                except ValueError as error:
                    rejected_lines.append(
                        f"Line {line_number}: {line} | Reason: {error}"
                    )
    except (FileNotFoundError, PermissionError, UnicodeDecodeError) as error:
        rejected_lines.append(f"Could not read input file: {error}")

    return report_lines, total_amount, rejected_lines


def main():
    output_folder = BASE_FOLDER / "output"
    output_folder.mkdir(exist_ok=True)
    report, total, rejected = prepare_mess_report(
        BASE_FOLDER / "input" / "mess_oct.txt"
    )

    with open(output_folder / "mess_report.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(report))
        file.write(f"\n\nTotal mess bill: Rs. {total:.2f}\n")

    with open(output_folder / "rejected_lines.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(rejected) if rejected else "No rejected lines.")
        file.write("\n")

    print("\n".join(report))
    print(f"Total mess bill: Rs. {total:.2f}")
    print("Rejected records:", len(rejected))


if __name__ == "__main__":
    main()
