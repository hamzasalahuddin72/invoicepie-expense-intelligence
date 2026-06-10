from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st

from parser import parse_invoice_pdf
from validator import validate_invoice
from duplicate_detector import load_invoice_records, compare_invoice_pair


DATABASE_PATH = Path("data/database/invoicepie.db")
UPLOAD_FOLDER = Path("data/uploaded_invoices")
EXISTING_RECORDS_FOLDER = "data/extracted_json"


def format_currency(value: float) -> str:
    """
    Format a number as GBP currency.
    """
    try:
        return f"£{float(value):,.2f}"
    except (TypeError, ValueError):
        return "£0.00"


@st.cache_data
def load_table(table_name: str) -> pd.DataFrame:
    """
    Load a known table from the SQLite database into a DataFrame.
    """
    allowed_tables = {
        "invoices",
        "validation_reports",
        "duplicate_matches",
    }

    if table_name not in allowed_tables:
        raise ValueError(f"Table not allowed: {table_name}")

    with sqlite3.connect(DATABASE_PATH) as connection:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", connection)


def save_uploaded_file(uploaded_file) -> Path:
    """
    Save an uploaded invoice PDF locally so it can be processed by the existing parser.
    """
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    safe_file_name = Path(uploaded_file.name).name
    upload_path = UPLOAD_FOLDER / safe_file_name

    with open(upload_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    return upload_path


def find_duplicate_matches_for_uploaded_invoice(parsed_invoice: dict) -> list[dict]:
    """
    Compare an uploaded invoice against existing parsed invoice records.
    """
    matches = []

    try:
        existing_records = load_invoice_records(EXISTING_RECORDS_FOLDER)
    except FileNotFoundError:
        return matches

    uploaded_record = parsed_invoice.copy()
    uploaded_record["_record_file"] = parsed_invoice.get("source_file", "uploaded_invoice.pdf")

    for existing_record in existing_records:
        match = compare_invoice_pair(uploaded_record, existing_record)

        if match:
            matches.append(match)

    return matches


def show_upload_processor() -> None:
    """
    Display file upload and single-invoice processing workflow.
    """
    st.header("Upload and Process a Single Invoice")

    st.write(
        "Upload a text-based invoice PDF to extract fields, run validation checks, "
        "and compare it against existing sample invoice records for possible duplicates."
    )

    uploaded_file = st.file_uploader(
        "Upload invoice PDF",
        type=["pdf"],
        help="Current MVP supports text-based PDF invoices. Scanned image invoices will need OCR later.",
    )

    if uploaded_file is None:
        st.info("Upload a PDF invoice to test single-invoice processing.")
        return

    if st.button("Process uploaded invoice"):
        try:
            upload_path = save_uploaded_file(uploaded_file)
            parsed_invoice = parse_invoice_pdf(str(upload_path))
            validation_report = validate_invoice(parsed_invoice)
            duplicate_matches = find_duplicate_matches_for_uploaded_invoice(parsed_invoice)

            st.success(f"Processed uploaded invoice: {uploaded_file.name}")

            st.subheader("Parsed Invoice Fields")
            st.json(parsed_invoice)

            st.subheader("Validation Result")

            validation_status = validation_report.get("validation_status")

            if validation_status == "passed":
                st.success("Validation passed. No issues found.")
            elif validation_status == "warning":
                st.warning("Validation completed with warnings.")
            else:
                st.error("Validation found high-risk issues. Review required.")

            st.json(validation_report)

            st.subheader("Duplicate Check")

            if duplicate_matches:
                st.warning(f"{len(duplicate_matches)} possible duplicate match found.")
                st.json(duplicate_matches)
            else:
                st.success("No duplicate matches found against existing records.")

        except Exception as error:
            st.error("Invoice processing failed.")
            st.exception(error)


def show_summary_metrics(
    invoices: pd.DataFrame,
    validation_reports: pd.DataFrame,
    duplicate_matches: pd.DataFrame,
) -> None:
    """
    Display the main dashboard summary metrics.
    """
    total_invoices = len(invoices)
    total_spend = invoices["total_amount"].sum() if not invoices.empty else 0

    unpaid_count = 0
    if not invoices.empty and "payment_status" in invoices.columns:
        unpaid_count = invoices["payment_status"].str.lower().eq("unpaid").sum()

    validation_issue_count = 0
    if not validation_reports.empty and "total_issues" in validation_reports.columns:
        validation_issue_count = int(validation_reports["total_issues"].sum())

    duplicate_count = len(duplicate_matches)

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Invoices", total_invoices)
    col2.metric("Total Spend", format_currency(total_spend))
    col3.metric("Unpaid Invoices", int(unpaid_count))
    col4.metric("Validation Issues", validation_issue_count)
    col5.metric("Duplicate Matches", duplicate_count)


def show_spend_insights(invoices: pd.DataFrame) -> None:
    """
    Display supplier and category spend insights.
    """
    st.subheader("Expense Insights")

    if invoices.empty:
        st.info("No invoice records available yet.")
        return

    category_spend = (
        invoices.groupby("category", dropna=False)["total_amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    supplier_spend = (
        invoices.groupby("supplier_name", dropna=False)["total_amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    st.write("Spend by Category")
    st.bar_chart(category_spend, x="category", y="total_amount")

    st.write("Spend by Supplier")
    st.bar_chart(supplier_spend, x="supplier_name", y="total_amount")


def show_invoice_table(invoices: pd.DataFrame) -> None:
    """
    Display stored invoice records.
    """
    st.subheader("Stored Invoice Records")

    if invoices.empty:
        st.info("No invoice records found.")
        return

    columns_to_show = [
        "supplier_name",
        "invoice_number",
        "invoice_date",
        "due_date",
        "subtotal",
        "vat_amount",
        "total_amount",
        "payment_status",
        "category",
        "source_file",
    ]

    available_columns = [column for column in columns_to_show if column in invoices.columns]
    st.dataframe(invoices[available_columns], width="stretch")


def show_validation_reports(validation_reports: pd.DataFrame) -> None:
    """
    Display validation results.
    """
    st.subheader("Validation Reports")

    if validation_reports.empty:
        st.info("No validation reports found.")
        return

    columns_to_show = [
        "supplier_name",
        "invoice_number",
        "validation_status",
        "total_issues",
        "high_risk_issues",
        "medium_risk_issues",
        "source_file",
    ]

    available_columns = [column for column in columns_to_show if column in validation_reports.columns]
    st.dataframe(validation_reports[available_columns], width="stretch")


def show_duplicate_matches(duplicate_matches: pd.DataFrame) -> None:
    """
    Display duplicate invoice warnings.
    """
    st.subheader("Duplicate Invoice Warnings")

    if duplicate_matches.empty:
        st.success("No duplicate matches found.")
        return

    columns_to_show = [
        "match_type",
        "similarity_score",
        "record_a_file",
        "record_b_file",
        "supplier_a",
        "supplier_b",
        "invoice_number_a",
        "invoice_number_b",
        "total_amount_a",
        "total_amount_b",
    ]

    available_columns = [column for column in columns_to_show if column in duplicate_matches.columns]
    st.dataframe(duplicate_matches[available_columns], width="stretch")


def show_existing_dashboard() -> None:
    """
    Display existing database-backed dashboard.
    """
    st.header("Expense Intelligence Dashboard")

    if not DATABASE_PATH.exists():
        st.warning(
            "Database file not found. Run `python app/database.py` first to create and populate the SQLite database."
        )
        st.stop()

    invoices = load_table("invoices")
    validation_reports = load_table("validation_reports")
    duplicate_matches = load_table("duplicate_matches")

    show_summary_metrics(invoices, validation_reports, duplicate_matches)

    st.divider()

    show_spend_insights(invoices)

    st.divider()

    show_invoice_table(invoices)

    st.divider()

    show_validation_reports(validation_reports)

    st.divider()

    show_duplicate_matches(duplicate_matches)


def main() -> None:
    """
    Run the InvoicePie dashboard and upload workflow.
    """
    st.set_page_config(
        page_title="InvoicePie Dashboard",
        page_icon="🧾",
        layout="wide",
    )

    st.title("InvoicePie — Expense Intelligence Dashboard")

    st.write(
        "InvoicePie extracts invoice data, validates parsed fields, detects duplicate invoices "
        "and presents expense insights through a dashboard."
    )

    upload_tab, dashboard_tab = st.tabs(
        ["Upload Invoice", "Dashboard"]
    )

    with upload_tab:
        show_upload_processor()

    with dashboard_tab:
        show_existing_dashboard()


if __name__ == "__main__":
    main()
