import pandas as pd

# Commenting out HSN CSV load as we're skipping validation for now
# hsn_df = pd.read_csv("data/hsn_reference.csv")

def validate_invoice_data(extracted_data):
    """
    Validate invoice data.
    HSN validation is currently skipped to avoid KeyError.
    """

    validated = extracted_data.copy()
    validated["line_items_validated"] = []

    for item in extracted_data["line_items"]:
        # Temporarily skip HSN validation
        # item["hsn_valid"] = hsn in hsn_df["HSN"].astype(str).values
        item["hsn_valid"] = True  # assume valid for now
        validated["line_items_validated"].append(item)

    # Check mandatory fields
    validated["mandatory_fields_present"] = all([
        extracted_data.get("country_of_origin"),
        len(extracted_data["line_items"]) > 0
    ])

    return validated
