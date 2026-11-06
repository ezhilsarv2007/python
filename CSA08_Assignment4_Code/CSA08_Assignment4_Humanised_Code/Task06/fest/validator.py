class InvalidRegistration(Exception):
    """Raised when a registration row contains invalid information."""


def validate_line(line):
    parts = line.strip().split(",")
    if len(parts) != 5:
        raise InvalidRegistration(f"Expected 5 fields, found {len(parts)}")

    register_number, name, department, email, event_text = parts
    if not register_number or not name or not department:
        raise InvalidRegistration("Register number, name and department are required")
    if "@" not in email or "." not in email.split("@")[-1] or email.startswith("@"):
        raise InvalidRegistration(f"Invalid email address: {email}")

    events = [event.strip() for event in event_text.split(";") if event.strip()]
    if not events:
        raise InvalidRegistration("At least one event must be selected")

    return {
        "register": register_number,
        "name": name,
        "department": department,
        "email": email,
        "events": events,
    }
