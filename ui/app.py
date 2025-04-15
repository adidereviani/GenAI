import streamlit as st
import tempfile
from ocr.ocr_processor import extract_text_from_file
from extraction.extractor import extract_fields

def main():
    st.title("Bituach Leumi Form Extractor")

    uploaded_file = st.file_uploader("Upload a PDF or Image", type=["pdf", "png", "jpg", "jpeg"])

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name

        st.write("Extracting text...")
        ocr_text = extract_text_from_file(tmp_file_path)

        st.write("Text extracted:")
        st.write(ocr_text)

        st.write("Extracting fields via GPT...")
        fields_dict = extract_fields(ocr_text)

        st.write("Extracted JSON:")
        st.json(fields_dict)

if __name__ == "__main__":
    main()
