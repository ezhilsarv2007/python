from pathlib import Path
from attendance_utils import read_attendance, calculate_percentages, write_report

def main():
    folder = Path(__file__).parent
    records = read_attendance(folder / "input.txt")
    percentages = calculate_percentages(records)
    write_report(percentages, folder / "output" / "report.txt")
    print(percentages)

if __name__ == "__main__":
    main()
