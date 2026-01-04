
import pdfplumber
import camelot
import re
from app.ocr import ocr_pdf
from app.utils import extract_text_or_ocr


def extract_bol_data(file_path: str):
    """
    Extracts key fields from a Bill of Lading PDF.
    Works with scanned PDFs using OCR if needed.
    """
    bol_data = {
        "shipper": "",
        "consignee": "",
        "bill_of_lading_no": "",
        "port_of_loading": "",
        "port_of_discharge": "",
        "vessel": "",
        "date_of_issue": ""
    }


    text = extract_text_or_ocr(file_path, ocr_pdf).lower()


    def find(label):
        for line in text.splitlines():
            if label.lower() in line:
                return line.split(":", 1)[-1].strip()
        return ""


    bol_data["shipper"] = find("shipper")
    bol_data["consignee"] = find("consignee")
    bol_data["bill_of_lading_no"] = find("bill of lading no")
    bol_data["port_of_loading"] = find("port of loading")
    bol_data["port_of_discharge"] = find("port of discharge")
    bol_data["vessel"] = find("vessel")
    bol_data["date_of_issue"] = find("date of issue")

    return bol_data


def extract_invoice_data(file_path):
    data = {"line_items": [], "country_of_origin": "", "other_attributes": {}}


    with pdfplumber.open(file_path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)

        country_match = re.search(r"Country of Origin:\s*(\w+)", text, re.IGNORECASE)
        if country_match:
            data["country_of_origin"] = country_match.group(1)


        invoice_no_match = re.search(r"Invoice Number:\s*([A-Z0-9\-]+)", text, re.IGNORECASE)
        if invoice_no_match:
            data["invoice_number"] = invoice_no_match.group(1)

        # Invoice date
        invoice_date_match = re.search(r"Invoice Date:\s*([\d\-A-Za-z]+)", text, re.IGNORECASE)
        if invoice_date_match:
            data["invoice_date"] = invoice_date_match.group(1)

        # Exporter / Importer
        exporter_match = re.search(r"Exporter:\s*(.+)", text, re.IGNORECASE)
        if exporter_match:
            data["exporter"] = exporter_match.group(1).strip()

        importer_match = re.search(r"Importer:\s*(.+)", text, re.IGNORECASE)
        if importer_match:
            data["importer"] = importer_match.group(1).strip()


    try:
        tables = camelot.read_pdf(file_path, pages="all", flavor="stream")
        for table in tables:
            df = table.df

            if "HSN" in df.to_string():
                headers = df.iloc[0].tolist()
                for idx, row in df.iloc[1:].iterrows():
                    item = {headers[i]: row[i] for i in range(len(headers))}
                    data["line_items"].append(item)
    except Exception as e:
        print(f"Error extracting table: {e}")

    return data