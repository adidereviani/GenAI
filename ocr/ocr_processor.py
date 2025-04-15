from .ocr_client import document_analysis_client


def extract_text_from_file(file_path: str) -> str:
    with open(file_path, "rb") as f:
        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-layout",
            document=f
        )
        result = poller.result()

    text_content = []
    for page in result.pages:
        for line in page.lines:
            text_content.append(line.content)

    return "\n".join(text_content)
