"""Utility functions for loading and applying styles across the application."""

import streamlit as st


def load_css_file(css_file_path):
    """
    Load CSS from file and return its content.
    
    :param css_file_path: Path to the CSS file
    :return: CSS content as string
    """
    with open(css_file_path, "r", encoding="utf-8") as f:
        css_content = f.read()
    return css_content


def apply_styles(css_file_path="style/styles.css"):
    """
    Apply CSS styles from file to the streamlit app.
    
    :param css_file_path: Path to the CSS file - defaults to main styles.css
    """
    css_content = load_css_file(css_file_path)
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
