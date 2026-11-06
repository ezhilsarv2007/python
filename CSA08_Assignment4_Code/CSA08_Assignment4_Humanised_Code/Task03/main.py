import os
import tempfile


class InvalidRecord(Exception):
    """Raised when an attendance line is not in the expected format."""


def parse_line(line):
    parts = line.strip().split(",")
    if len(parts) != 3:
        raise InvalidRecord(f"Expected 3 fields, found {len(parts)}")

    register_number, date, status = parts
    if status not in ("P", "A"):
        raise InvalidRecord(f"Invalid attendance status: {status}")

    return register_number, date, status


def summarise(path):
    present = 0
    absent = 0
    errors = []

    try:
        with open(path, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if not line.strip():
                    continue
                try:
                    register_number, date, status = parse_line(line)
                    if status == "P":
                        present += 1
                    else:
                        absent += 1
                except InvalidRecord as error:
                    errors.append((line_number, str(error)))
    except (FileNotFoundError, PermissionError, UnicodeDecodeError) as error:
        raise RuntimeError("Could not process the attendance file") from error
    else:
        print("Attendance file processed successfully.")
    finally:
        print("File processing attempt finished.")

    return present, absent, errors


def main():
    sample_data = (
        "192311001,2026-10-08,P\n"
        "192311002,2026-10-08,A\n"
        "192311003,2026-10-08\n"
        "192311004,2026-10-08,L\n"
    )
    with tempfile.NamedTemporaryFile(
        "w", suffix=".csv", delete=False, encoding="utf-8"
    ) as temp_file:
        temp_file.write(sample_data)
        file_name = temp_file.name

    try:
        print("Summary:", summarise(file_name))
    finally:
        os.remove(file_name)

    try:
        summarise("missing_attendance_file.csv")
    except RuntimeError as error:
        print(error)
        print("Original cause:", type(error.__cause__).__name__)


if __name__ == "__main__":
    main()
