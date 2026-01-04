# app/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import os
import pandas as pd

from app.classifier import classify_document
from app.extractor import extract_invoice_data, extract_bol_data
from app.validator import validate_invoice_data
from app.transformer import export_to_excel, submit_to_customs
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Logistics Document Processing Platform")


from app.transformer import export_to_excel

@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    results = []

    for file in files:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())

        doc_type = classify_document(file_location)

        if doc_type == "Invoice":
            data = extract_invoice_data(file_location)
            validated_data = validate_invoice_data(data)
            results.append({"filename": file.filename, "type": doc_type, "data": validated_data})

        elif doc_type == "Bill of Lading":
            data = extract_bol_data(file_location)
            results.append({"filename": file.filename, "type": doc_type, "data": data})

        else:
            results.append({"filename": file.filename, "type": doc_type, "data": None})


    export_to_excel(results, filename="validated_documents.xlsx")

    return results


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <h1>Logistics Document Processing</h1>
    <form action="/upload" enctype="multipart/form-data" method="post">
        <input name="files" type="file" multiple>
        <input type="submit" value="Upload">
    </form>
    """
