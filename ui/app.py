import json
import os
import sys
import tempfile
import time

import streamlit as st
from streamlit_extras.stylable_container import stylable_container

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from ocr.ocr_processor import extract_text_from_file
from extraction.extractor import extract_fields
from extraction.validator import validate_fields

st.set_page_config(page_title="🏛️ חילוץ טפסי ביטוח לאומי", layout="wide")

# Language selection
lang = st.sidebar.selectbox("🌐 Choose Language / בחר שפה", ("עברית", "English"))

# UI translations
translations = {
    "English": {
        "title": "🏛️ Bituach Leumi Form Extractor",
        "upload_header": "Upload Your Form 📄",
        "upload_file": "Choose a PDF or JPG",
        "caption": "Built with ❤️ by Adi Prager",
        "scanning": "🔍 Scanning the document...",
        "extracting": "📝 Extracting fields...",
        "validating": "🛡️ Validating extracted data...",
        "done": "✅ Done!",
        "success": "All done! Here are your results:",
        "extracted_data": "📄 Extracted JSON Data",
        "validation_results": "🛡️ Validation Results",
        "validation_errors": "⚠️ View Validation Errors",
        "validation_detected": "Validation issues detected. Download the report for details.",
        "validation_passed": "🎯 All fields passed validation checks!",
        "download_data": "📥 Download Extracted Data",
        "download_json": "📄 Download JSON File",
        "download_validation": "📥 Download Validation Report",
        "upload_prompt": "Please upload a PDF or JPG file to get started."
    },
    "עברית": {
        "title": "🏛️ חילוץ טפסי ביטוח לאומי",
        "upload_header": "העלה את הטופס שלך 📄",
        "upload_file": "בחר קובץ PDF או JPG",
        "caption": "נבנה באהבה ❤️ על ידי עדי פרגר",
        "scanning": "🔍 סורק את המסמך...",
        "extracting": "📝 מחלץ שדות...",
        "validating": "🛡️ מאמת נתונים...",
        "done": "✅ הסתיים!",
        "success": "הכול מוכן! הנה התוצאות:",
        "extracted_data": "📄 נתוני JSON שהופקו",
        "validation_results": "🛡️ תוצאות אימות הנתונים",
        "validation_errors": "⚠️ הצג שגיאות אימות",
        "validation_detected": "נמצאו בעיות אימות בנתונים. ניתן להוריד את הדוח לפרטים נוספים.",
        "validation_passed": "🎯 כל השדות עברו אימות בהצלחה!",
        "download_data": "📥 הורדת נתונים מופקים",
        "download_json": "📄 הורדת קובץ JSON",
        "download_validation": "📥 הורדת דוח אימות",
        "upload_prompt": "נא להעלות קובץ PDF או JPG כדי להתחיל."
    }
}

t = translations[lang]

# Set page text direction based on language
if lang == "עברית":
    st.markdown("""
        <style>
        .stApp {
            direction: rtl;
            text-align: right;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp {
            direction: ltr;
            text-align: left;
        }
        </style>
    """, unsafe_allow_html=True)

st.title(t["title"])

# Sidebar for file upload
with st.sidebar:
    st.header(t["upload_header"])
    uploaded = st.file_uploader(t["upload_file"])
    st.markdown("---")
    st.caption(t["caption"])

progress_placeholder = st.empty()

if uploaded:
    # Save uploaded file temporarily
    ext = os.path.splitext(uploaded.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(uploaded.read())
        tmp_path = tmp.name

    # OCR processing and field extraction with progress updates
    progress = progress_placeholder.progress(0, text=t["scanning"])
    time.sleep(0.5)
    ocr_txt = extract_text_from_file(tmp_path)
    progress.progress(40, text=t["extracting"])
    time.sleep(0.5)
    data = extract_fields(ocr_txt)
    progress.progress(70, text=t["validating"])
    errs = validate_fields(data)
    progress.progress(100, text=t["done"])
    time.sleep(0.5)
    progress_placeholder.empty()

    st.success(t["success"])

    # Display extracted JSON data
    st.subheader(t["extracted_data"])
    with stylable_container(key="json_container", css_styles="background-color: #f9f9f9; padding: 1rem; border-radius: 10px;"):
        st.json(data, expanded=True)

    # Display validation results
    st.subheader(t["validation_results"])
    if errs:
        with st.expander(t["validation_errors"], expanded=False):
            st.json(errs, expanded=False)
        st.error(t["validation_detected"])
        st.download_button(
            t["download_validation"],
            json.dumps(errs, ensure_ascii=False, indent=2),
            "validation_report.json",
            "application/json",
            use_container_width=True
        )
    else:
        st.success(t["validation_passed"])

    # Download extracted data
    st.subheader(t["download_data"])
    st.download_button(
        t["download_json"],
        json.dumps(data, ensure_ascii=False, indent=2),
        "extracted.json",
        "application/json",
        use_container_width=True
    )
else:
    # If no file is uploaded, show an informational message
    with stylable_container(key="info_box", css_styles="background-color: #eef6ff; padding: 1rem; border-radius: 10px;"):
        st.info(t["upload_prompt"])
