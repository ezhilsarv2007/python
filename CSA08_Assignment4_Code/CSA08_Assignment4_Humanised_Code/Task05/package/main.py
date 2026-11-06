from pathlib import Path
from attendance.reader import read_attendance
from attendance.stats import calculate_percentages
from attendance.report import write_report

def main():
    folder = Path(__file__).parent
    records = read_attendance(folder / "input.txt")
    percentages = calculate_percentages(records)
    write_report(percentages, folder / "output" / "report.txt")
    print(percentages)

if __name__ == "__main__":
    main()
