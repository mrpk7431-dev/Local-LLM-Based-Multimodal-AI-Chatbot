import streamlit as st
import uuid
from services.ollama import get_installed_models
from services.chat import get_all_chats, save_chat, delete_chat, load_chat
from config import DEFAULT_MODEL

def render_sidebar():
    with st.sidebar:
        st.title("🤖 Local AI Chat")
        
        # New Chat Button
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.current_chat_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()
            
        st.divider()
        
        # Model Selection
        models = get_installed_models()
        if not models:
            st.error("⚠️ Ollama is not running!")
            st.markdown(
                "<div style='font-size:0.85rem; color:#bbb; margin-bottom:10px; line-height:1.4;'>"
                "When you restart your laptop, the AI engine stops. <br><br>"
                "<b>Fix:</b> Open the <b>Ollama</b> app from your Windows Start Menu, wait a few seconds, then click Retry below."
                "</div>", 
                unsafe_allow_html=True
            )
            if st.button("🔄 Retry Connection", type="primary", use_container_width=True):
                st.rerun()
            selected_model = DEFAULT_MODEL
        else:
            default_index = models.index(DEFAULT_MODEL) if DEFAULT_MODEL in models else 0
            selected_model = st.selectbox("Select Model", models, index=default_index)
            
        st.session_state.selected_model = selected_model
        
        # Settings Panel
        with st.expander("⚙️ Settings"):
            st.session_state.temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=0.7, step=0.1)
            st.session_state.max_tokens = st.number_input("Max Tokens", min_value=128, max_value=8192, value=2048, step=128)
            st.session_state.stream = st.toggle("Stream Response", value=True)
            
        # Removed Attachments section from sidebar


        st.divider()
        
        # Chat History
        st.subheader("Chat History")
        chats = get_all_chats()
        
        for chat in chats:
            col1, col2 = st.columns([4, 1])
            with col1:
                # Truncate title
                title = chat['title'][:25] + "..." if len(chat['title']) > 25 else chat['title']
                if st.button(f"💬 {title}", key=f"btn_{chat['id']}", use_container_width=True):
                    loaded = load_chat(chat['id'])
                    if loaded:
                        st.session_state.current_chat_id = loaded['id']
                        st.session_state.messages = loaded.get('messages', [])
                        st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{chat['id']}", help="Delete chat"):
                    delete_chat(chat['id'])
                    if st.session_state.get("current_chat_id") == chat['id']:
                        st.session_state.current_chat_id = str(uuid.uuid4())
                        st.session_state.messages = []
                    st.rerun()
