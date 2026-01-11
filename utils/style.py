import streamlit as st

def apply_style():
    st.markdown("""
        <style>
        body {
            font-family: 'Segoe UI', sans-serif;
        }
        </style>
    """, unsafe_allow_html=True)

