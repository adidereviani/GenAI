import re
from .ocr_client import document_analysis_client

def extract_text_from_file(file_path: str) -> str:
    """
    Performs OCR on a National Insurance form using Azure Document Intelligence.
    Returns cleaned, human-readable text with normalized date and number formats.
    """
    with open(file_path, "rb") as f:
        poller = document_analysis_client.begin_analyze_document(
            model_id="prebuilt-layout",
            document=f,
            locale="he-IL",
        )
    result = poller.result()

    # Extract text lines from each page
    lines = [line.content for page in result.pages for line in page.lines]
    text = "\n".join(lines)

    # Clean the extracted text
    text = text.replace("|", "")
    text = re.sub(
        r"\b(?:\d\s+){3,}\d\b",
        lambda m: m.group(0).replace(" ", ""),
        text
    )

    # Normalize date formats from noisy OCR results
    def _norm_date(match):
        digits = re.sub(r"\D", "", match.group(0))
        if len(digits) == 8:
            return f" {digits[:2]} {digits[2:4]} {digits[4:]}"
        return match.group(0)

    text = re.sub(r"\b(?:[\d\W]*\d){8}\b", _norm_date, text)

    return text
