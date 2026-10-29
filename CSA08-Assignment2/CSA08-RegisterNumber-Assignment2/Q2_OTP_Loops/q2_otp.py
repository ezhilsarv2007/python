"""Q2: Bank kiosk OTP verification."""

CORRECT_OTP = "4821"


def verify_with_while(entries):
    print("WHILE LOOP")
    attempt = 0
    index = 0
    while attempt < 3 and index < len(entries):
        entered = entries[index]
        index += 1
        if entered == "":
            print("Blank entry: please enter the OTP. Attempt not counted.")
            continue
        attempt += 1
        if entered == CORRECT_OTP:
            print("OTP correct. Login successful.")
            break
        print("Wrong OTP. Attempts used:", attempt)
    else:
        print("Account locked for 30 minutes.")


def verify_with_for(entries):
    print("\nFOR LOOP")
    for attempt in range(3):
        if attempt >= len(entries):
            print("No OTP entered.")
            continue
        entered = entries[attempt]
        if entered == "":
            print("Blank entry: please enter the OTP.")
            pass  # Placeholder for a future audit-log action.
            continue
        if entered == CORRECT_OTP:
            print("OTP correct. Login successful.")
            break
        print("Wrong OTP. Attempts used:", attempt + 1)
    else:
        print("Account locked for 30 minutes.")


def verify_with_security(entries, security_correct):
    print("\nCHANGED RULE: SECURITY QUESTION")
    allowed_attempts = 5 if security_correct else 3
    attempt = 0
    index = 0
    while attempt < allowed_attempts and index < len(entries):
        entered = entries[index]
        index += 1
        if entered == "":
            print("Blank entry ignored.")
            continue
        attempt += 1
        if entered == CORRECT_OTP:
            print("OTP correct. Login successful.")
            break
        print("Wrong OTP. Attempts used:", attempt)
    else:
        print("Account locked for 30 minutes.")


if __name__ == "__main__":
    sample = ["", "1111", "2222", "3333"]
    verify_with_while(sample)
    verify_with_for(["1111", "2222", "3333"])
    verify_with_security(["1111", "2222", "3333", "4444", "4821"], True)
