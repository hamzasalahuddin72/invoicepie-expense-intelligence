from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st

from parser import parse_invoice_pdf
from validator import validate_invoice
from duplicate_detector import load_invoice_records, compare_invoice_pair
from database import (
    connect_database,
    create_tables,
    reset_tables,
    import_invoice_records,
    import_validation_reports,
    import_duplicate_reports,
)


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
                st.warning(f"{len(duplicate_matches)} possible duplicate match(es) found.")
                st.json(duplicate_matches)
            else:
                st.success("No duplicate matches found against existing records.")

        except Exception as error:
            st.error("Invoice processing failed.")
            st.exception(error)


def add_review_columns(
    invoices: pd.DataFrame,
    validation_reports: pd.DataFrame,
    duplicate_matches: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add validation and duplicate review information to invoice records.
    """
    invoices = invoices.copy()

    if invoices.empty:
        return invoices

    if not validation_reports.empty:
        validation_columns = [
            "source_file",
            "validation_status",
            "total_issues",
            "high_risk_issues",
            "medium_risk_issues",
        ]

        available_validation_columns = [
            column for column in validation_columns if column in validation_reports.columns
        ]

        invoices = invoices.merge(
            validation_reports[available_validation_columns],
            on="source_file",
            how="left",
        )
    else:
        invoices["validation_status"] = "not_validated"
        invoices["total_issues"] = 0
        invoices["high_risk_issues"] = 0
        invoices["medium_risk_issues"] = 0

    for column in ["validation_status", "total_issues", "high_risk_issues", "medium_risk_issues"]:
        if column not in invoices.columns:
            if column == "validation_status":
                invoices[column] = "not_validated"
            else:
                invoices[column] = 0

    duplicate_record_files = set()

    if not duplicate_matches.empty:
        for column in ["record_a_file", "record_b_file"]:
            if column in duplicate_matches.columns:
                duplicate_record_files.update(
                    duplicate_matches[column].dropna().astype(str).tolist()
                )

    if "record_file" in invoices.columns:
        invoices["duplicate_risk"] = invoices["record_file"].astype(str).apply(
            lambda record_file: "Duplicate risk"
            if record_file in duplicate_record_files
            else "No duplicate risk"
        )
    else:
        invoices["duplicate_risk"] = "No duplicate risk"

    return invoices


def sorted_unique_values(dataframe: pd.DataFrame, column: str) -> list[str]:
    """
    Return sorted unique non-empty values from a DataFrame column.
    """
    if dataframe.empty or column not in dataframe.columns:
        return []

    values = (
        dataframe[column]
        .dropna()
        .astype(str)
        .str.strip()
    )

    values = values[values != ""]

    return sorted(values.unique().tolist())


def apply_dashboard_filters(invoices: pd.DataFrame) -> pd.DataFrame:
    """
    Display dashboard filters and return filtered invoice records.
    """
    if invoices.empty:
        return invoices

    st.subheader("Review Filters")

    with st.expander("Filter invoice records", expanded=True):
        col1, col2, col3 = st.columns(3)

        suppliers = sorted_unique_values(invoices, "supplier_name")
        categories = sorted_unique_values(invoices, "category")
        payment_statuses = sorted_unique_values(invoices, "payment_status")

        selected_suppliers = col1.multiselect(
            "Supplier",
            suppliers,
            default=suppliers,
        )

        selected_categories = col2.multiselect(
            "Category",
            categories,
            default=categories,
        )

        selected_payment_statuses = col3.multiselect(
            "Payment Status",
            payment_statuses,
            default=payment_statuses,
        )

        col4, col5, col6 = st.columns(3)

        validation_statuses = sorted_unique_values(invoices, "validation_status")
        duplicate_risks = sorted_unique_values(invoices, "duplicate_risk")

        selected_validation_statuses = col4.multiselect(
            "Validation Status",
            validation_statuses,
            default=validation_statuses,
        )

        selected_duplicate_risks = col5.multiselect(
            "Duplicate Risk",
            duplicate_risks,
            default=duplicate_risks,
        )

        invoice_search = col6.text_input(
            "Search invoice number or supplier",
            placeholder="Example: INV-1001 or ABC Hotel",
        )

    filtered = invoices.copy()

    if selected_suppliers:
        filtered = filtered[filtered["supplier_name"].astype(str).isin(selected_suppliers)]

    if selected_categories:
        filtered = filtered[filtered["category"].astype(str).isin(selected_categories)]

    if selected_payment_statuses:
        filtered = filtered[filtered["payment_status"].astype(str).isin(selected_payment_statuses)]

    if selected_validation_statuses:
        filtered = filtered[filtered["validation_status"].astype(str).isin(selected_validation_statuses)]

    if selected_duplicate_risks:
        filtered = filtered[filtered["duplicate_risk"].astype(str).isin(selected_duplicate_risks)]

    if invoice_search.strip():
        search_value = invoice_search.strip().lower()

        supplier_match = filtered["supplier_name"].astype(str).str.lower().str.contains(search_value)
        invoice_match = filtered["invoice_number"].astype(str).str.lower().str.contains(search_value)

        filtered = filtered[supplier_match | invoice_match]

    st.caption(f"Showing {len(filtered)} of {len(invoices)} invoice records after filters.")

    return filtered


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
    if not invoices.empty and "total_issues" in invoices.columns:
        validation_issue_count = int(invoices["total_issues"].fillna(0).sum())

    duplicate_count = 0
    if not invoices.empty and "duplicate_risk" in invoices.columns:
        duplicate_count = invoices["duplicate_risk"].eq("Duplicate risk").sum()

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Invoices", total_invoices)
    col2.metric("Total Spend", format_currency(total_spend))
    col3.metric("Unpaid Invoices", int(unpaid_count))
    col4.metric("Validation Issues", validation_issue_count)
    col5.metric("Duplicate Risk Records", int(duplicate_count))


def show_spend_insights(invoices: pd.DataFrame) -> None:
    """
    Display supplier and category spend insights.
    """
    st.subheader("Expense Insights")

    if invoices.empty:
        st.info("No invoice records match the selected filters.")
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


def show_review_sections(invoices: pd.DataFrame) -> None:
    """
    Display focused review sections for invoices that need attention.
    """
    st.subheader("Review Sections")

    if invoices.empty:
        st.info("No invoice records match the selected filters.")
        return

    needs_review = invoices[
        (invoices["validation_status"].astype(str).str.lower() != "passed")
        | (invoices["duplicate_risk"].astype(str) == "Duplicate risk")
    ]

    unpaid_invoices = invoices[
        invoices["payment_status"].astype(str).str.lower().isin(["unpaid", "pending", "overdue"])
    ]

    col1, col2 = st.columns(2)

    with col1:
        st.write("Invoices Needing Review")

        if needs_review.empty:
            st.success("No invoices need review in the selected filter view.")
        else:
            review_columns = [
                "supplier_name",
                "invoice_number",
                "validation_status",
                "total_issues",
                "duplicate_risk",
                "total_amount",
                "source_file",
            ]

            available_columns = [column for column in review_columns if column in needs_review.columns]
            st.dataframe(needs_review[available_columns], width="stretch")

    with col2:
        st.write("Unpaid / Pending Invoices")

        if unpaid_invoices.empty:
            st.success("No unpaid or pending invoices in the selected filter view.")
        else:
            unpaid_columns = [
                "supplier_name",
                "invoice_number",
                "due_date",
                "payment_status",
                "total_amount",
                "category",
                "source_file",
            ]

            available_columns = [column for column in unpaid_columns if column in unpaid_invoices.columns]
            st.dataframe(unpaid_invoices[available_columns], width="stretch")


def show_invoice_table(invoices: pd.DataFrame) -> None:
    """
    Display stored invoice records.
    """
    st.subheader("Filtered Invoice Records")

    if invoices.empty:
        st.info("No invoice records found for the selected filters.")
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
        "validation_status",
        "total_issues",
        "duplicate_risk",
        "source_file",
    ]

    available_columns = [column for column in columns_to_show if column in invoices.columns]
    st.dataframe(invoices[available_columns], width="stretch")


def show_validation_reports(validation_reports: pd.DataFrame, filtered_invoices: pd.DataFrame) -> None:
    """
    Display validation results for filtered invoices.
    """
    st.subheader("Validation Reports")

    if validation_reports.empty:
        st.info("No validation reports found.")
        return

    filtered_source_files = set(filtered_invoices["source_file"].dropna().astype(str).tolist())

    if filtered_source_files and "source_file" in validation_reports.columns:
        validation_reports = validation_reports[
            validation_reports["source_file"].astype(str).isin(filtered_source_files)
        ]

    if validation_reports.empty:
        st.info("No validation reports match the selected filters.")
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


def show_duplicate_matches(duplicate_matches: pd.DataFrame, filtered_invoices: pd.DataFrame) -> None:
    """
    Display duplicate invoice warnings relevant to the filtered invoice records.
    """
    st.subheader("Duplicate Invoice Warnings")

    if duplicate_matches.empty:
        st.success("No duplicate matches found.")
        return

    filtered_record_files = set(filtered_invoices["record_file"].dropna().astype(str).tolist())

    if filtered_record_files:
        duplicate_matches = duplicate_matches[
            duplicate_matches["record_a_file"].astype(str).isin(filtered_record_files)
            | duplicate_matches["record_b_file"].astype(str).isin(filtered_record_files)
        ]

    if duplicate_matches.empty:
        st.success("No duplicate matches found for the selected filters.")
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

    with st.expander("Duplicate match explanations"):
        for index, match in duplicate_matches.iterrows():
            st.write(
                f"Match {index + 1}: {match.get('record_a_file')} ↔ {match.get('record_b_file')}"
            )
            st.write(f"Similarity score: {match.get('similarity_score')}")


def ensure_database_exists() -> None:
    """
    Create and populate the local SQLite database if it does not already exist.

    This helps the app run correctly in deployment environments where the local
    database file is not committed to GitHub.
    """
    if DATABASE_PATH.exists():
        return

    connection = connect_database(str(DATABASE_PATH))
    create_tables(connection)
    reset_tables(connection)
    import_invoice_records(connection, "data/extracted_json")
    import_validation_reports(connection, "data/validation_reports")
    import_duplicate_reports(connection, "data/duplicate_reports")
    connection.close()


def show_existing_dashboard() -> None:
    """
    Display existing database-backed dashboard with filters and review UI.
    """
    st.header("Expense Intelligence Dashboard")

    ensure_database_exists()

    if st.button("Refresh dashboard data"):
        st.cache_data.clear()
        st.rerun()

    invoices = load_table("invoices")
    validation_reports = load_table("validation_reports")
    duplicate_matches = load_table("duplicate_matches")

    invoices = add_review_columns(invoices, validation_reports, duplicate_matches)

    filtered_invoices = apply_dashboard_filters(invoices)

    st.divider()

    show_summary_metrics(filtered_invoices, validation_reports, duplicate_matches)

    st.divider()

    show_review_sections(filtered_invoices)

    st.divider()

    show_spend_insights(filtered_invoices)

    st.divider()

    show_invoice_table(filtered_invoices)

    st.divider()

    show_validation_reports(validation_reports, filtered_invoices)

    st.divider()

    show_duplicate_matches(duplicate_matches, filtered_invoices)


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

