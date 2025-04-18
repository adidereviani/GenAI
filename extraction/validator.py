from __future__ import annotations

import re
from datetime import datetime
from typing import Dict, Any

from .json_template import JSON_TEMPLATE

def _only_digits(s: str) -> str:
    """Removes all non-digit characters from the given string."""
    return re.sub(r"\D", "", s)

def _valid_id(num: str) -> bool:
    """Validates an Israeli ID number using the official checksum algorithm."""
    num = _only_digits(num).zfill(9)
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

def _valid_date(d: Dict[str, str]) -> bool:
    """Checks if a date dictionary with day, month, and year is a valid date."""
    try:
        if all(d.get(x) for x in ("day", "month", "year")):
            datetime.strptime("{day}/{month}/{year}".format(**d), "%d/%m/%Y")
            return True
    except Exception:
        pass
    return False

def _valid_mobile(phone: str) -> bool:
    """Validates that the phone number matches the Israeli mobile format (05xxxxxxxx)."""
    return bool(re.fullmatch(r"05\d{8}", phone))

def _valid_landline(phone: str) -> bool:
    """Validates that the phone number matches the Israeli landline format (0[2-9]xxxxxxx)."""
    return bool(re.fullmatch(r"0[2-9]\d{7}", phone))

def validate_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validates extracted data fields against expected formats and constraints.
    Returns a dictionary mapping field paths to specific error messages."""
    errors: Dict[str, Any] = {}

    def check_missing_fields(template: Dict[str, Any], actual: Dict[str, Any], path: str = ""):
        """Recursively checks for missing fields based on the JSON template."""
        for key, value in template.items():
            full_key = f"{path}.{key}" if path else key
            if isinstance(value, dict):
                check_missing_fields(value, actual.get(key, {}), full_key)
            else:
                if actual.get(key, "") == "":
                    errors[full_key] = {"error": "Missing value"}

    check_missing_fields(JSON_TEMPLATE, data)

    if not _valid_id(data.get("idNumber", "")):
        errors["idNumber"] = {"error": "Invalid Israeli ID number"}

    if not _valid_date(data.get("dateOfBirth", {})):
        errors["dateOfBirth"] = {"error": "Invalid date"}

    mob = data.get("mobilePhone", "")
    if mob and not _valid_mobile(mob):
        errors["mobilePhone"] = {"error": "Invalid mobile format (05xxxxxxxx)"}

    land = data.get("landlinePhone", "")
    if land and not _valid_landline(land):
        errors["landlinePhone"] = {"error": "Invalid landline format"}

    if gender := data.get("gender", ""):
        if gender not in {"זכר", "נקבה", "Male", "Female"}:
            errors["gender"] = {"error": "Unrecognised gender value"}

    return errors
