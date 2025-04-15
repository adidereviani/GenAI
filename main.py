from dotenv import load_dotenv
load_dotenv()

import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

endpoint = os.getenv("FORM_RECOGNIZER_ENDPOINT")
key = os.getenv("FORM_RECOGNIZER_KEY")

print("Endpoint:", endpoint)
print("Key:", key)


document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)

# A small sample test – analyzing layout from a PDF or image file
with open("/Users/prager/PycharmProjects/GenAI/phase1_data/283_ex1.pdf", "rb") as f:
    poller = document_analysis_client.begin_analyze_document("prebuilt-layout", document=f)
    result = poller.result()

print("Analyze result:")
for page in result.pages:
    print(f"Page number: {page.page_number}, width: {page.width}, height: {page.height}")


import uvicorn

if __name__ == "__main__":
    uvicorn.run("ui.app:app", host="0.0.0.0", port=8000, reload=True)
