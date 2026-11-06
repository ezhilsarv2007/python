import random
import time

def normalise_number(number):
    # Keep digits only, so +91 98400-12345 and 9840012345 are comparable.
    digits = "".join(character for character in str(number) if character.isdigit())
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    return digits

def normalise_name(name):
    return " ".join(str(name).lower().replace(".", " ").split())

def merge_contacts(contact_lists):
    merged = {}

    for contact in contact_lists:
        name = contact.get("name", "").strip()
        email = contact.get("email", "").strip().lower()
        raw_numbers = contact.get("numbers", [])

        # Accept either one phone number or a list of phone numbers.
        if isinstance(raw_numbers, str):
            raw_numbers = [raw_numbers]

        clean_numbers = {normalise_number(number) for number in raw_numbers}
        clean_numbers.discard("")

        # Use each number as a lookup key. Contacts without a number get a
        # separate name-based key, since there is no number to match.
        keys = clean_numbers or {"name:" + normalise_name(name)}
        existing_keys = [key for key in keys if key in merged]

        if existing_keys:
            main_key = existing_keys[0]
            record = merged[main_key]
        else:
            main_key = next(iter(keys))
            record = {"name": name, "numbers": set(), "emails": set()}
            merged[main_key] = record

        if name and not record["name"]:
            record["name"] = name
        record["numbers"].update(clean_numbers)
        if email:
            record["emails"].add(email)

        # Make every number point to the same merged contact.
        for key in keys:
            merged[key] = record

    # Return each contact only once, even if several numbers point to it.
    unique_records = []
    seen = set()
    for record in merged.values():
        identity = id(record)
        if identity not in seen:
            seen.add(identity)
            unique_records.append({
                "name": record["name"],
                "numbers": sorted(record["numbers"]),
                "emails": sorted(record["emails"])
            })
    return sorted(unique_records, key=lambda item: item["name"].lower())

old_phone = [
    {"name": "Dr. Ravi", "numbers": ["+91 98400 12345"], "email": "ravi@example.com"},
    {"name": "Meena", "numbers": ["9000011111"], "email": "meena@example.com"},
]
new_phone = [
    {"name": "ravi kumar", "numbers": ["9840012345", "9888812345"], "email": "RAVI@EXAMPLE.COM"},
    {"name": "Meena", "numbers": ["+91-90000-11111"], "email": ""},
    {"name": "Arun", "numbers": [], "email": "arun@example.com"},
]

result = merge_contacts(old_phone + new_phone)
print("Merged contacts:")
for contact in result:
    print(contact)

# A small hand-check: Ravi should appear once with two numbers.
ravi = next(contact for contact in result if "ravi" in contact["name"].lower())
assert len(ravi["numbers"]) == 2
print("Small test passed:", ravi)

# Timing experiment using unique contacts.
for size in (1000, 100000):
    sample = [
        {"name": f"Person {i}", "numbers": [f"90000{i:05d}"], "email": ""}
        for i in range(size)
    ]
    start = time.perf_counter()
    merged_sample = merge_contacts(sample)
    elapsed = time.perf_counter() - start
    print(f"{size} contacts merged in {elapsed:.5f}s; output records={len(merged_sample)}")
