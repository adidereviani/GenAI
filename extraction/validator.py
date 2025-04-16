import re
from datetime import datetime

def is_valid_id(id_number: str) -> bool:
    num = re.sub(r"\D", "", id_number).zfill(9)
    if len(num) != 9:
        return False
    total = 0
    for i, digit in enumerate(num):
        factor = 1 if i % 2 == 0 else 2
        product = int(digit) * factor
        if product > 9:
            product -= 9
        total += product
    return total % 10 == 0


def is_valid_date(d: dict) -> bool:
    try:
        if d.get("day") and d.get("month") and d.get("year"):
            datetime.strptime(f"{d['day']}/{d['month']}/{d['year']}", "%d/%m/%Y")
            return True
    except Exception:
        pass
    return False

def is_valid_mobile_phone(phone: str) -> bool:
    # Valid Israeli mobile numbers must be exactly 10 digits and start with "05".
    return bool(re.fullmatch(r"05\d{8}", phone)) if phone else True

def is_valid_landline_phone(phone: str) -> bool:
    # Israeli landline numbers typically start with 0 and have 9 digits (e.g., 0[2-9] followed by 7 digits).
    return bool(re.fullmatch(r"0[2-9]\d{7}", phone)) if phone else True

def extract_and_fix_digits(text: str) -> str:
    # Fix sequences of digits with spaces and missing prefixes
    text = re.sub(r"\b(\d ?){8,11}\b", lambda m: m.group(0).replace(' ', ''), text)

    # Fix mobile numbers missing 05 prefix
    text = re.sub(r"(?<!\d)([4-9]\d{7})(?!\d)", r"05\1", text)

    # Clean landline numbers with correct prefix
    text = re.sub(r"(?<!\d)(0[2-9]\d{7})(?!\d)", lambda m: m.group(1).replace(' ', ''), text)

    return text

def validate_fields(data: dict) -> dict:
    errors = {}
    id_number = data.get("idNumber", "")
    if not is_valid_id(id_number):
        errors["idNumber"] = {
            "error": "Invalid ID. Israeli ID must be 9 digits and valid per checksum.",
            "suggestion": f"Try padding with zero: {id_number.zfill(9)}"
        }

    if not is_valid_date(data.get("dateOfBirth", {})):
        errors["dateOfBirth"] = {"error": "Invalid date of birth"}

    mobile = data.get("mobilePhone", "")
    if mobile and not is_valid_mobile_phone(mobile):
        errors["mobilePhone"] = {
            "error": "Invalid mobile format.",
            "suggestion": f"Ensure it starts with 05 and has 10 digits. Got: {mobile}"
        }

    landline = data.get("landlinePhone", "")
    if landline and not is_valid_landline_phone(landline):
        errors["landlinePhone"] = {"error": "Invalid landline format."}

    return errors
