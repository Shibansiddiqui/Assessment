import pdfplumber

def extract_text_or_ocr(pdf_path, ocr_func):
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

    if len(text.strip()) < 50:
        # Probably scanned PDF
        return ocr_func(pdf_path)

    return text
