import os
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Load environment variables from a .env file
load_dotenv()

# Retrieve Form Recognizer credentials from environment variables
endpoint = os.getenv("FORM_RECOGNIZER_ENDPOINT")
key = os.getenv("FORM_RECOGNIZER_KEY")

# Validate that both endpoint and key are set
if not endpoint or not key:
    raise EnvironmentError("FORM_RECOGNIZER credentials not set in environment")

# Initialize the Azure Form Recognizer client with the retrieved credentials
document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key),
)
