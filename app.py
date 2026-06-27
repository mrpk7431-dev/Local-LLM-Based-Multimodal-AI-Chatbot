import streamlit as st
import os
import uuid
from ui.sidebar import render_sidebar
from ui.chat_interface import render_chat_interface

# Page Configuration
st.set_page_config(
    page_title="Local AI ChatBot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "styles", "main.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def init_session():
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []

def main():
    load_css()
    init_session()
    
    render_sidebar()
    render_chat_interface()

if __name__ == "__main__":
    main()
