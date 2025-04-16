# In your UI code (ui/app.py), modify the temporary file creation so that the original file extension is preserved:
import sys
import os
import json
import tempfile
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ocr.ocr_processor import extract_text_from_file
from extraction.extractor import extract_fields
from extraction.validator import validate_fields

def main():
    st.title("Bituach Leumi Form Extractor")
    uploaded_file = st.file_uploader("Upload a PDF or Image", type=["pdf", "png", "jpg", "jpeg"])

    if uploaded_file is not None:
        file_ext = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name

        st.write("🔍 Extracting text...")
        ocr_text = extract_text_from_file(tmp_file_path)
        # ocr_text = extract_text_with_tesseract(tmp_file_path)

        st.subheader("📄 Text Extracted from OCR")
        st.text_area("OCR Output", ocr_text, height=250)

        st.write("🤖 Extracting fields via GPT...")
        fields_dict = extract_fields(ocr_text)

        st.subheader("🧾 Extracted JSON")
        st.json(fields_dict)

        st.subheader("✅ Field Validation")
        errors = validate_fields(fields_dict)

        if errors:
            st.error("Some fields failed validation:")
            for field, msg in errors.items():
                st.markdown(f"**{field}**: {msg}")
        else:
            st.success("All fields passed validation 🎉")

        st.download_button(
            label="📥 Download Extracted JSON",
            data=json.dumps(fields_dict, indent=2, ensure_ascii=False),
            file_name="extracted_data.json",
            mime="application/json"
        )

if __name__ == "__main__":
    main()
