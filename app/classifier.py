import ollama
import pdfplumber

client = ollama.Client()


def classify_document(file_path: str) -> str:
    text = ""

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages[:2]:   # ONLY first 2 pages
            if page.extract_text():
                text += page.extract_text() + "\n"

    prompt = f"""
You are a document classifier.

Classify the following logistics document into ONE of these types:
- Invoice
- Bill of Lading
- Packing List
- Unknown

Return ONLY the document type name.
No explanation.

Document text:
{text[:1500]}
"""

    response = client.generate(
        model="llama3:latest",
        prompt=prompt
    )

    result = response["response"].strip().lower()

    if "invoice" in result:
        return "Invoice"
    if "bill of lading" in result or "b/l" in result:
        return "Bill of Lading"
    if "packing" in result:
        return "Packing List"

    return "Unknown"
