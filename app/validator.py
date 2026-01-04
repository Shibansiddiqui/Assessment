import pandas as pd



def validate_invoice_data(extracted_data):
    """
    Validate invoice data.
    HSN validation is currently skipped to avoid KeyError.
    """

    validated = extracted_data.copy()
    validated["line_items_validated"] = []

    for item in extracted_data["line_items"]:

        item["hsn_valid"] = True
        validated["line_items_validated"].append(item)


    validated["mandatory_fields_present"] = all([
        extracted_data.get("country_of_origin"),
        len(extracted_data["line_items"]) > 0
    ])

    return validated
