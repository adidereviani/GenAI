import os
import json
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_type = "azure"
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_version = os.getenv("OPENAI_API_VERSION")

def extract_fields(ocr_text: str) -> dict:
    """
    Sends OCR text to Azure OpenAI (GPT) with a prompt that asks for JSON-structured
    field extraction. Returns a dictionary with the extracted fields.
    """

    prompt = f"""
    You are an assistant that extracts structured fields from the text below.
    The desired format is JSON with these fields:
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

    Only respond with valid JSON, no extra text.

    Text to analyze:
    \"\"\"{ocr_text}\"\"\"
    """

    response = openai.Completion.create(
        engine="YOUR_GPT_DEPLOYMENT_NAME",
        prompt=prompt,
        max_tokens=1500,
        temperature=0
    )

    raw_output = response["choices"][0]["text"].strip()
    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError:
        data = {}

    return data
