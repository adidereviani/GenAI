import re
from typing import List, Optional
from extraction.validator import _valid_id, _valid_mobile

def _candidates(txt: str, length: int) -> List[str]:
    """Finds digit groups in the text that approximately match the expected length (±2 characters)."""
    return re.findall(rf"\b\d[ \d]{{{length-1},{length+2}}}\b", txt)

def normalise(num: str) -> str:
    """Normalizes a number string by collapsing repeated consecutive digits often caused by OCR noise.
    Example: '11 33 777' becomes '137'."""
    return re.sub(r"(\d)\1{1,}", r"\1", num)

def best_israeli_id(txt: str) -> Optional[str]:
    """Finds the best matching valid ID number from the given text."""
    for raw in _candidates(txt, 9):
        num = normalise(re.sub(r"\D", "", raw))
        if len(num) == 9 and _valid_id(num):
            return num
    return None

def best_mobile(txt: str) -> Optional[str]:
    """Finds the best matching valid mobile phone number from the given text."""
    for raw in _candidates(txt, 10):
        num = normalise(re.sub(r"\D", "", raw))
        if len(num) == 10 and num.startswith("05") and _valid_mobile(num):
            return num
    return None
