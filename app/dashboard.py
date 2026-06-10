import streamlit as st

from dashboard_data import load_dashboard_data, load_table
from dashboard_views import (
    show_filters,
    show_summary_metrics,
    show_review_sections,
    show_expense_insights,
    show_invoice_table,
    show_validation_reports,
    show_duplicate_matches,
)
from upload_processor import show_upload_processor


def show_dashboard():
    st.header("Expense Intelligence Dashboard")

    if st.button("Refresh dashboard data"):
        st.cache_data.clear()
        st.rerun()

    invoices, validation_reports, duplicate_matches = load_dashboard_data()

    filtered_invoices = show_filters(invoices)

    st.divider()
    show_summary_metrics(filtered_invoices)

    st.divider()
    show_review_sections(filtered_invoices)

    st.divider()
    show_expense_insights(filtered_invoices)

    st.divider()
    show_invoice_table(filtered_invoices)

    st.divider()
    show_validation_reports(validation_reports, filtered_invoices)

    st.divider()
    show_duplicate_matches(duplicate_matches, filtered_invoices)


def main():
    st.set_page_config(
        page_title="InvoicePie Dashboard",
        page_icon="🥧",
        layout="wide",
    )

    st.title("InvoicePie — Expense Intelligence Dashboard")

    st.write(
        "InvoicePie extracts invoice data, validates parsed fields, detects duplicate invoices "
        "and presents expense insights through a dashboard."
    )

    upload_tab, dashboard_tab = st.tabs(["Upload Invoice", "Dashboard"])

    with upload_tab:
        show_upload_processor()

    with dashboard_tab:
        show_dashboard()


if __name__ == "__main__":
    main()
