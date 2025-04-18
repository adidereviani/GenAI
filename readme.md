# 🏛️ Bituach Leumi Form Extractor

A full pipeline to **OCR**, **extract**, **correct**, and **validate** structured data from scanned **National Insurance forms** (Bituach Leumi) using:
- **Azure Document Intelligence (OCR)**
- **OpenAI GPT (field extraction)**
- **Streamlit (frontend app)**

---

## 📦 Project Structure

```
GenAI/
├── extraction/
│   ├── __init__.py
│   ├── extractor.py
│   ├── id_phone_helpers.py
│   ├── json_template.py
│   └── validator.py
├── ocr/
│   ├── __init__.py
│   ├── ocr_client.py
│   └── ocr_processor.py
├── phase1_data/
│   ├── 283_ex1.pdf
│   ├── 283_ex2.pdf
│   ├── 283_ex3.pdf
│   └── 283_raw.pdf
├── ui/
│   ├── __init__.py
│   └── app.py
├── .env
├── requirements.txt
└── readme.md
```

---

## ⚙️ How it Works

1. **OCR Text Extraction**  
   `ocr_processor.py` uses Azure's `DocumentAnalysisClient` to scan a PDF/JPG form and outputs human-readable text.

2. **Field Extraction**  
   `extractor.py` prompts GPT-4o (via Azure OpenAI) to extract structured fields into a predefined JSON schema.

3. **Post-Processing & Corrections**  
   - Fixes OCR errors in Israeli IDs and mobile numbers.
   - Normalizes dates and phone formats.

4. **Validation**  
   `validator.py` checks:
   - Valid Israeli ID
   - Correct mobile and landline phone formats
   - Proper date structure
   - Recognized gender labels

5. **User Interface**  
   `ui/app.py` provides an interactive web UI to upload a form, track progress, view results, and download JSON and validation reports.

---

## 🛠️ Requirements

- Python 3.9+
- Azure Form Recognizer resource
- Azure OpenAI resource
- `.env` file with:

```dotenv
FORM_RECOGNIZER_ENDPOINT=your-form-recognizer-endpoint
FORM_RECOGNIZER_KEY=your-form-recognizer-key
OPENAI_API_KEY=your-azure-openai-key
OPENAI_API_BASE=your-azure-openai-endpoint
OPENAI_API_VERSION=your-openai-api-version
```

- Install dependencies:

```bash
pip install -r requirements.txt
```

Example `requirements.txt`:
```
streamlit==1.18.1
protobuf==3.20.3
click==8.1.3
azure-ai-formrecognizer==3.3.0
azure-common==1.1.28
azure-core==1.33.0
python-dotenv==0.20.0
openai==0.27.0
altair==4.2.0
azure-core>=1.29.4
pdf2image==1.17.0
streamlit-extras
python-multipart
Pillow
pytesseract
```

---

## 🚀 Running the App

```bash
streamlit run ui/app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🌐 Language Support

- **English** 🇬🇧
- **עברית (Hebrew)** 🇮🇱

Select your preferred language from the sidebar!

---

## 📋 Features

- 🧐 **Intelligent OCR and Field Mapping**
- 🔍 **Auto-repair common OCR mistakes**
- 🛡️ **Validation engine for data integrity**
- 💬 **Bilingual user interface (LTR/RTL support)**
- 📥 **Download structured JSON and error reports**

---

## ❤️ Built By

Adi Prager

---

