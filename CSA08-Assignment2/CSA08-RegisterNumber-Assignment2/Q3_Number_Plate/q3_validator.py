"""Q3: Normalise, validate and format vehicle registration numbers."""


def normalise(text):
    """Remove spaces and hyphens, then use capital letters."""
    text = text.strip().upper()
    text = text.replace(" ", "")
    text = text.replace("-", "")
    return text


def is_valid(reg):
    """Check the registration structure using slicing and string methods."""
    if len(reg) != 9 and len(reg) != 10:
        return False

    state = reg[0:2]
    district = reg[2:4]
    last_four = reg[-4:]
    series = reg[4:-4]

    if len(series) != 1 and len(series) != 2:
        return False

    return (state.isalpha() and district.isdigit()
            and series.isalpha() and last_four.isdigit())


def format_receipt(reg):
    """Format a valid registration for a receipt."""
    if not is_valid(reg):
        return "Invalid registration"
    return reg[0:2] + " " + reg[2:4] + " " + reg[4:-4] + " " + reg[-4:]


samples = [
    "tn 09 ab 1234",
    "KA-01-M-0007",
    "TN9AB1234",
    "TN 22 1234 AB",
    "mh 12 xy 9876",
    "1234 TN AB 09",
]

print("REGISTRATION VALIDATOR")
for raw in samples:
    reg = normalise(raw)
    status = "valid" if is_valid(reg) else "INVALID"
    print(raw, "->", reg, status)
    if is_valid(reg):
        print("Receipt:", format_receipt(reg))

print("\nString note: strings are immutable, so upper() returns a new string.")
print("For a 10-character plate, s[-4:] gives the last four characters.")
print("For a 10-character plate, s[4:-4] gives the two-character series.")
