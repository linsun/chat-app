import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome V2! 👋")

st.sidebar.success("Select an option from the sidebar.")

st.header(
    """
    **👈 Select a demo from the sidebar** to see some demos!
"""
)
