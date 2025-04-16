# Updated extraction function with enhanced instructions (extraction/extractor.py)
import os
import json
import re
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_type = "azure"
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_version = os.getenv("OPENAI_API_VERSION")

DEPLOYMENT_NAME = "gpt-4o"


def extract_fields(ocr_text: str) -> dict:
    system_message = (
        "You are a JSON-generating assistant. Return only valid JSON with no extra explanation. "
        "Output must be enclosed in a triple backtick code block. "
        "Do NOT translate values — preserve them exactly as they appear (in Hebrew or English). "
        "Use the following field names in English, matching the structure exactly as below."
    )

    user_prompt = f"""
        Extract all fields from the form content below.
        Preserve field names in Hebrew exactly as they appear in the form (e.g., "שם משפחה", "תאריך לידה").
        For date fields, use objects with "יום", "חודש", "שנה" as keys.
        
        - "שם משפחה" → "lastName"
        - "שם פרטי" → "firstName"
        - "מספר זהות" → "idNumber"
        - "מין" → "gender"
        - "תאריך לידה" → "dateOfBirth"
        - "כתובת" → "address"
          - "רחוב" → "street"
          - "מספר בית" → "houseNumber"
          - "כניסה" → "entrance"
          - "דירה" → "apartment"
          - "ישוב" → "city"
          - "מיקוד" → "postalCode"
          - "תא דואר" → "poBox"
        - "טלפון קווי" → "landlinePhone"
        - "טלפון נייד" → "mobilePhone"
        - "סוג העבודה" → "jobType"
        - "תאריך הפגיעה" → "dateOfInjury"
        - "שעת הפגיעה" → "timeOfInjury"
        - "מקום התאונה" → "accidentLocation"
        - "כתובת מקום התאונה" → "accidentAddress"
        - "תיאור התאונה" → "accidentDescription"
        - "האיבר שנפגע" → "injuredBodyPart"
        - "חתימה" → "signature"
        - "תאריך מילוי הטופס" → "formFillingDate"
        - "תאריך קבלת הטופס בקופה" → "formReceiptDateAtClinic"
        - "חבר בקופת חולים" → "medicalInstitutionFields.healthFundMember"
        - "מהות התאונה" → "medicalInstitutionFields.natureOfAccident"
        - "אבחנות רפואיות" → "medicalInstitutionFields.medicalDiagnoses"

        Extract the fields from the OCR text below and output a JSON object with the structure below.
        For numeric fields like "idNumber" and "mobilePhone", extract all digits exactly as they appear in the form.
        The "idNumber" field may contain 9 or 10 digits as it appears.
        The "mobilePhone" field must include its full prefix (e.g. "05").

        JSON structure:
        {{
          "lastName": "",
          "firstName": "",
          "idNumber": "",
          "gender": "",
          "dateOfBirth": {{
            "day": "",
            "month": "",
            "year": ""
          }},
          "address": {{
            "street": "",
            "houseNumber": "",
            "entrance": "",
            "apartment": "",
            "city": "",
            "postalCode": "",
            "poBox": ""
          }},
          "landlinePhone": "",
          "mobilePhone": "",
          "jobType": "",
          "dateOfInjury": {{
            "day": "",
            "month": "",
            "year": ""
          }},
          "timeOfInjury": "",
          "accidentLocation": "",
          "accidentAddress": "",
          "accidentDescription": "",
          "injuredBodyPart": "",
          "signature": "",
          "formFillingDate": {{
            "day": "",
            "month": "",
            "year": ""
          }},
          "formReceiptDateAtClinic": {{
            "day": "",
            "month": "",
            "year": ""
          }},
          "medicalInstitutionFields": {{
            "healthFundMember": "",
            "natureOfAccident": "",
            "medicalDiagnoses": ""
          }}
        }}

        OCR Text:
        \"\"\"{ocr_text}\"\"\"

        Return a JSON dictionary matching the structure of the form in Hebrew.
        Wrap your response in a code block.
        """

    try:
        response = openai.ChatCompletion.create(
            engine=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,
            max_tokens=1800
        )

        raw_output = response["choices"][0]["message"]["content"].strip()
        match = re.search(r"```json\s*(\{.*?\})\s*```", raw_output, re.DOTALL)
        json_text = match.group(1) if match else raw_output
        return correct_common_field_errors(json.loads(json_text))
    except Exception as e:
        return {"error": "Failed to extract fields", "details": str(e)}


def correct_common_field_errors(data):
    if len(data.get('idNumber', '')) == 8:
        data['idNumber'] = '0' + data['idNumber']
    if data.get('mobilePhone', '') and not data['mobilePhone'].startswith('05'):
        data['mobilePhone'] = '05' + data['mobilePhone']
    return data
