import re

from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageOps
import pytesseract
import os
import tempfile

from extraction.validator import extract_and_fix_digits
from ocr.ocr_client import document_analysis_client

def convert_pdf_to_images(file_path: str, dpi: int = 500) -> list:
    return convert_from_path(file_path, dpi=dpi)

def preprocess_image(image: Image.Image) -> Image.Image:
    gray = ImageOps.grayscale(image)
    contrast = ImageEnhance.Contrast(gray).enhance(3.0)
    sharp = ImageEnhance.Sharpness(contrast).enhance(3.5)
    inverted = ImageOps.invert(sharp)
    threshold = 180
    binary = inverted.point(lambda p: 255 if p > threshold else 0)
    return binary

def clean_ocr_text(ocr_text: str) -> str:
    # Fix common OCR issues with digits and Hebrew/English confusion
    ocr_text = re.sub(r"(?<=\d) (?=\d)", '', ocr_text)  # join split digits
    ocr_text = ocr_text.replace('O', '0').replace('I', '1').replace('l', '1')

    # Extract and fix ID and phone number formats
    ocr_text = extract_and_fix_digits(ocr_text)

    ocr_text = re.sub(r"[^א-תa-zA-Z0-9\s,:.\-\\/]", '', ocr_text)  # remove noise
    return ocr_text

def extract_text_with_tesseract(file_path: str) -> str:
    images = convert_pdf_to_images(file_path) if file_path.lower().endswith(".pdf") else [Image.open(file_path)]
    full_text = ""
    for img in images:
        preprocessed = preprocess_image(img)
        text = pytesseract.image_to_string(preprocessed, lang="heb+eng")
        full_text += text + "\n"
    return clean_ocr_text(full_text)

def extract_text_from_file(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    text_lines = []
    try:
        if ext == ".pdf":
            images = convert_pdf_to_images(file_path, dpi=500)
            for image in images:
                preprocessed = preprocess_image(image)
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_img:
                    preprocessed.save(tmp_img.name, "PNG")
                    with open(tmp_img.name, "rb") as f:
                        poller = document_analysis_client.begin_analyze_document(
                            model_id="prebuilt-document",
                            document=f
                        )
                        result = poller.result()
                        for page in result.pages:
                            for line in page.lines:
                                text_lines.append(line.content)
        else:
            with open(file_path, "rb") as f:
                poller = document_analysis_client.begin_analyze_document(
                    model_id="prebuilt-document",
                    document=f
                )
                result = poller.result()
                for page in result.pages:
                    for line in page.lines:
                        text_lines.append(line.content)

        azure_text = clean_ocr_text("\n".join(text_lines).strip())
        tesseract_text = extract_text_with_tesseract(file_path)
        return azure_text if len(azure_text) > len(tesseract_text) else tesseract_text

    except Exception:
        return extract_text_with_tesseract(file_path)

    except Exception as e:
        print(f"⚠️ Azure OCR failed or produced poor results. Error: {e}")
        return extract_text_with_tesseract(file_path)