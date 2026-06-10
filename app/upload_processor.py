from pathlib import Path

import streamlit as st

from parser import parse_invoice_pdf
from validator import validate_invoice
from duplicate_detector import load_invoice_records, compare_invoice_pair


UPLOAD_FOLDER = Path("data/uploaded_invoices")
EXISTING_RECORDS_FOLDER = "data/extracted_json"


def save_uploaded_file(uploaded_file):
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    file_name = Path(uploaded_file.name).name
    file_path = UPLOAD_FOLDER / file_name

    with open(file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    return file_path


def find_duplicate_matches(parsed_invoice):
    matches = []

    try:
        existing_records = load_invoice_records(EXISTING_RECORDS_FOLDER)
    except FileNotFoundError:
        return matches

    uploaded_record = parsed_invoice.copy()
    uploaded_record["_record_file"] = parsed_invoice.get("source_file", "uploaded_invoice.pdf")

    for record in existing_records:
        match = compare_invoice_pair(uploaded_record, record)

        if match:
            matches.append(match)

    return matches


def show_upload_processor():
    st.header("Upload and Process a Single Invoice")

    st.write(
        "Upload a text-based invoice PDF to extract fields, run validation checks, "
        "and compare it against existing invoice records."
    )

    uploaded_file = st.file_uploader(
        "Upload invoice PDF",
        type=["pdf"],
        help="This MVP supports text-based PDFs. Scanned invoices need OCR later.",
    )

    if uploaded_file is None:
        st.info("Upload a PDF invoice to test single-invoice processing.")
        return

    if not st.button("Process uploaded invoice"):
        return

    try:
        file_path = save_uploaded_file(uploaded_file)

        parsed_invoice = parse_invoice_pdf(str(file_path))
        validation_report = validate_invoice(parsed_invoice)
        duplicate_matches = find_duplicate_matches(parsed_invoice)

        st.success(f"Processed uploaded invoice: {uploaded_file.name}")

        st.subheader("Parsed Invoice Fields")
        st.json(parsed_invoice)

        st.subheader("Validation Result")
        show_validation_message(validation_report)
        st.json(validation_report)

        st.subheader("Duplicate Check")
        show_duplicate_message(duplicate_matches)

    except Exception as error:
        st.error("Invoice processing failed.")
        st.exception(error)


def show_validation_message(validation_report):
    status = validation_report.get("validation_status")

    if status == "passed":
        st.success("Validation passed. No issues found.")
    elif status == "warning":
        st.warning("Validation completed with warnings.")
    else:
        st.error("Validation found high-risk issues. Review required.")


def show_duplicate_message(duplicate_matches):
    if duplicate_matches:
        st.warning(f"{len(duplicate_matches)} possible duplicate match(es) found.")
        st.json(duplicate_matches)
    else:
        st.success("No duplicate matches found against existing records.")
