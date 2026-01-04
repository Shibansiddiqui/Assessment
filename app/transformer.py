import pandas as pd
import os

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def transform_to_excel(validated_data, original_filename):
    df = pd.DataFrame(validated_data["line_items_validated"])
    excel_path = os.path.join(OUTPUT_DIR, original_filename.replace(".pdf", ".xlsx"))
    df.to_excel(excel_path, index=False)
    return excel_path


import pandas as pd
import requests

def submit_to_customs(data, endpoint_url):
    """Submit structured JSON to customs API."""
    headers = {"Content-Type": "application/json"}
    response = requests.post(endpoint_url, json=data, headers=headers)
    return response.status_code, response.json()


def export_to_excel(all_documents, filename="validated_documents.xlsx"):
    invoice_rows = []
    bol_rows = []

    for doc in all_documents:
        if doc['data'] is None:
            continue

        if doc['type'] == "Invoice":
            line_items = doc['data'].get("line_items", [])
            for item in line_items:
                row = {
                    "Filename": doc['filename'],
                    "Invoice Number": doc['data'].get("invoice_number", ""),
                    "Date": doc['data'].get("invoice_date", ""),
                    "Exporter": doc['data'].get("exporter", ""),
                    "Importer": doc['data'].get("importer", ""),
                    "Country of Origin": doc['data'].get("country_of_origin", ""),
                    "Item Description": item.get("Item Description", ""),
                    "HSN": item.get("HSN Code", ""),
                    "Quantity": item.get("Quantity", ""),
                    "Unit Price": item.get("Unit Price (USD)", "")
                }
                invoice_rows.append(row)

        elif doc['type'] == "Bill of Lading":
            row = {
                "Filename": doc['filename'],
                "BOL Number": doc['data'].get("bill_of_lading_no", ""),
                "Shipper": doc['data'].get("shipper", ""),
                "Consignee": doc['data'].get("consignee", ""),
                "Port of Loading": doc['data'].get("port_of_loading", ""),
                "Port of Discharge": doc['data'].get("port_of_discharge", ""),
                "Vessel": doc['data'].get("vessel", ""),
                "Date of Issue": doc['data'].get("date_of_issue", "")
            }
            bol_rows.append(row)


    if not invoice_rows and not bol_rows:
        print("No data to export to Excel")
        return

    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        if invoice_rows:
            pd.DataFrame(invoice_rows).to_excel(writer, sheet_name="Invoices", index=False)
        if bol_rows:
            pd.DataFrame(bol_rows).to_excel(writer, sheet_name="BOLs", index=False)

    print(f"Excel exported: {filename}")