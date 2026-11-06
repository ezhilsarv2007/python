def read_attendance(file_name):
    records = []
    with open(file_name, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split(",")
            if len(parts) == 3 and parts[2] in ("P", "A"):
                records.append(parts)
    return records
