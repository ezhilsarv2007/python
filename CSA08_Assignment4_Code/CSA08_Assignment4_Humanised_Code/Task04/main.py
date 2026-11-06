from pathlib import Path

BASE_FOLDER = Path(__file__).parent
OUTPUT_FOLDER = BASE_FOLDER / "output"
RETURN_LOG = OUTPUT_FOLDER / "returns.log"
ERROR_LOG = OUTPUT_FOLDER / "error.log"


def save_returns(book_names):
    with open(RETURN_LOG, "a", encoding="utf-8") as file:
        for book_name in book_names:
            if book_name.strip():
                file.write(book_name.strip() + "\n")


def process_day(day_file):
    try:
        with open(day_file, "r", encoding="utf-8") as file:
            book_names = file.readlines()
        save_returns(book_names)
    except (FileNotFoundError, PermissionError, UnicodeDecodeError) as error:
        with open(ERROR_LOG, "a", encoding="utf-8") as file:
            file.write(
                f"{day_file.name}: {type(error).__name__}: {error}\n"
            )
        print("Could not process:", day_file.name)


def main():
    OUTPUT_FOLDER.mkdir(exist_ok=True)
    RETURN_LOG.write_text("", encoding="utf-8")
    ERROR_LOG.write_text("", encoding="utf-8")

    for day_name in ("day1.txt", "day2.txt", "day3.txt", "missing_day.txt"):
        process_day(BASE_FOLDER / "input" / day_name)

    print("Returned books:")
    print(RETURN_LOG.read_text(encoding="utf-8"))
    print("Error log:")
    print(ERROR_LOG.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
