from __future__ import annotations

import json
import os
import time
from copy import deepcopy
from typing import Any, Dict

import openai
from dotenv import load_dotenv

from extraction.id_phone_helpers import best_israeli_id, best_mobile
from extraction.validator import _valid_id, _valid_mobile
from .json_template import JSON_TEMPLATE

# Load environment variables from a .env file
load_dotenv()

# Setup OpenAI API credentials
openai.api_type = "azure"
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_version = os.getenv("OPENAI_API_VERSION")
_DEPLOYMENT = "gpt-4o"

# Define mappings between English and Hebrew labels
LABEL_ALIASES = {
    "Last name": "שם משפחה",
    "First name": "שם פרטי",
    "Date of birth": "תאריך לידה",
    "ID number": "מספר זהות",
    "Gender": "מין",
}

# Template for the system prompt to instruct the LLM
_PROMPT_TEMPLATE = """
You are a JSON‑generating assistant. Return **only** valid JSON and nothing else – no markdown.
The JSON **must** match exactly the structure shown below; if a field is missing, output an empty string.

{aliases}

Extract the fields from the OCR text delimited by triple quotes and populate the template.
"""

# Build the alias instruction block for the prompt
alias_lines = [f'- "{eng}" maps to the Hebrew label "{heb}"' for eng, heb in LABEL_ALIASES.items()]
alias_block = "English ↔ Hebrew aliases:\n" + "\n".join(alias_lines)
_PROMPT = _PROMPT_TEMPLATE.format(aliases=alias_block)

def _deep_update(dst: Dict[str, Any], src: Dict[str, Any]) -> None:
    """Recursively updates the destination dictionary with values from the source dictionary.
    Preserves structure from the destination and fills missing values from the source or leaves them empty."""
    for k, v in dst.items():
        if isinstance(v, dict):
            _deep_update(v, src.get(k, {}))
        else:
            dst[k] = src.get(k, "")

def extract_fields(ocr_text: str) -> Dict[str, Any]:
    """Extracts structured fields from OCR text using an LLM.
    Ensures the output matches the required JSON template and applies post-processing corrections."""
    system_msg = {
        "role": "system",
        "content": "You are a helpful assistant that writes JSON strictly conforming to the required schema.",
    }
    user_msg = {
        "role": "user",
        "content": (
            f"{_PROMPT}\n\nTemplate:\n{json.dumps(JSON_TEMPLATE, ensure_ascii=False)}\n\n"
            f'"""' + ocr_text + '"""'
        ),
    }

    delay = 1.5
    for attempt in range(3):
        try:
            resp = openai.ChatCompletion.create(
                engine=_DEPLOYMENT,
                messages=[system_msg, user_msg],
                temperature=0,
                max_tokens=900,
            )
            raw = resp["choices"][0]["message"]["content"].strip()
            json_text = raw if raw.startswith("{") else raw.split("```")[-2]
            parsed = json.loads(json_text)

            full = deepcopy(JSON_TEMPLATE)
            _deep_update(full, parsed)

            if not _valid_id(full.get("idNumber", "")):
                if cand := best_israeli_id(ocr_text):
                    full["idNumber"] = cand

            mob = full.get("mobilePhone", "")
            if not _valid_mobile(mob):
                if cand := best_mobile(ocr_text):
                    full["mobilePhone"] = cand

            return _fix_common_errors(full)
        except Exception as exc:
            if attempt == 2:
                raise RuntimeError(f"LLM extraction failed: {exc}")
            time.sleep(delay)
            delay *= 2

def _fix_common_errors(d: Dict[str, Any]) -> Dict[str, Any]:
    """Performs minor deterministic corrections on extracted fields,
    such as padding ID numbers and correcting mobile phone prefixes."""
    if len(d.get("idNumber", "")) == 8:
        d["idNumber"] = "0" + d["idNumber"]
    phone = d.get("mobilePhone", "")
    if phone and not phone.startswith("05"):
        d["mobilePhone"] = "05" + phone.lstrip("0")
    return d
