import streamlit as st

def apply_style():
    st.markdown("""
        <style>
            /* Personnalisation du style */
            .stButton>button {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
            }
            .stDataFrame, .stTable {
                font-size: 14px;
            }
        </style>
    """, unsafe_allow_html=True)
