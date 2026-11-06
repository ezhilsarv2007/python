import csv
from pathlib import Path
from .reader import read_file
from .validator import validate_line, InvalidRegistration


def process_registrations(department_files, output_folder):
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    students = {}
    event_participants = {}
    errors = []

    for file_path in department_files:
        try:
            lines = read_file(file_path)
            for line_number, line in enumerate(lines, start=1):
                if not line.strip():
                    continue
                try:
                    student = validate_line(line)
                    register_number = student["register"]
                    if register_number in students:
                        errors.append(
                            f"{file_path.name}, line {line_number}: duplicate register {register_number}"
                        )
                        continue

                    students[register_number] = student
                    for event in student["events"]:
                        event_participants.setdefault(event, []).append(student)
                except InvalidRegistration as error:
                    errors.append(f"{file_path.name}, line {line_number}: {error}")
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as error:
            errors.append(f"{file_path.name}: {type(error).__name__}: {error}")

    with open(output_folder / "master_list.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Register Number", "Name", "Department", "Email", "Events"])
        for student in students.values():
            writer.writerow([
                student["register"], student["name"], student["department"],
                student["email"], ";".join(student["events"])
            ])

    event_folder = output_folder / "events"
    event_folder.mkdir(exist_ok=True)
    for event, participants in event_participants.items():
        safe_name = "".join(ch.lower() if ch.isalnum() else "_" for ch in event)
        with open(event_folder / f"{safe_name}.txt", "w", encoding="utf-8") as file:
            for student in participants:
                file.write(
                    f"{student['register']}, {student['name']}, {student['department']}\n"
                )

    with open(output_folder / "summary_report.txt", "w", encoding="utf-8") as file:
        file.write(f"Unique students: {len(students)}\n")
        file.write(f"Events: {len(event_participants)}\n")
        for event, participants in sorted(event_participants.items()):
            file.write(f"{event}: {len(participants)} participants\n")

    with open(output_folder / "error_log.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(errors) if errors else "No errors.")
        file.write("\n")

    return students, event_participants, errors
