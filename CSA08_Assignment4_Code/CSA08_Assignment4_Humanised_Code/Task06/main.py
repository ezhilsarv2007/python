from pathlib import Path
from fest.process import process_registrations


def main():
    base_folder = Path(__file__).parent
    department_files = [
        base_folder / "input" / "department_cse.txt",
        base_folder / "input" / "department_it.txt",
        base_folder / "input" / "department_ece.txt",  # missing file test
    ]

    students, events, errors = process_registrations(
        department_files, base_folder / "output"
    )
    print("Unique registrations:", len(students))
    print("Events:", ", ".join(sorted(events)))
    print("Errors recorded:", len(errors))


if __name__ == "__main__":
    main()
