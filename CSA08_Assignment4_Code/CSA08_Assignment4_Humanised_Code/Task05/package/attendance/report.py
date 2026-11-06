def write_report(percentages, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        for register_number, percentage in sorted(percentages.items()):
            file.write(f"{register_number}: {percentage:.2f}%\n")
