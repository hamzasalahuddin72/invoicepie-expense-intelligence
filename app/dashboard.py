from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st


DATABASE_PATH = Path("data/database/invoicepie.db")


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


def show_summary_metrics(invoices: pd.DataFrame, validation_reports: pd.DataFrame, duplicate_matches: pd.DataFrame) -> None:
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


def main() -> None:
    """
    Run the InvoicePie dashboard.
    """
    st.set_page_config(
        page_title="InvoicePie Dashboard",
        page_icon="🧾",
        layout="wide",
    )

    st.title("InvoicePie — Expense Intelligence Dashboard")

    st.write(
        "This dashboard shows invoice records, validation results and duplicate warnings "
        "generated by the InvoicePie document-processing pipeline."
    )

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


if __name__ == "__main__":
    main()
