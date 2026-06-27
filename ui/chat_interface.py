import streamlit as st
import time
import base64
from services.ollama import stream_chat
from services.chat import save_chat
from utils.helpers import format_timestamp
from utils.file_parser import extract_text_from_file

def render_chat_interface():
    # Initialize session state if needed
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Show attractive animated welcome header if chat is empty
    if not st.session_state.messages:
        st.markdown("""
            <div class="welcome-header">
                <h1><span class="gradient-text">Local AI</span> ChatBot</h1>
                <p>How can I help you today?</p>
            </div>
        """, unsafe_allow_html=True)
        

    # Display chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
            # If user message has extra context, just show a truncated version or original prompt
            if msg["role"] == "user" and "Here are the attached documents for context:" in msg["content"]:
                # Extract the actual prompt
                try:
                    display_content = msg["content"].split("User Question: ")[-1]
                    if display_content:
                        st.markdown(display_content)
                    st.caption("📎 Document(s) attached")
                except:
                    st.markdown(msg["content"])
            else:
                if msg["content"]:
                    st.markdown(msg["content"])
                
            if "images" in msg and msg["images"]:
                st.caption(f"📎 Attached {len(msg['images'])} image(s)")
            
    # Chat Input with File Upload (requires Streamlit >= 1.43.0)
    # Note: Streamlit's accept_file feature requires st.chat_input to handle the return object
    try:
        prompt_data = st.chat_input("Ask anything", accept_file="multiple", file_type=["png", "jpg", "jpeg", "pdf", "docx", "txt", "md", "csv"])
    except TypeError:
        # Fallback for older Streamlit versions that don't support accept_file
        prompt_data = st.chat_input("Ask anything (Update Streamlit to >=1.43.0 for inline file uploads)")

    if prompt_data:
        # Handle both the new object (Streamlit >= 1.43) and old string return type
        prompt_text = getattr(prompt_data, "text", prompt_data if isinstance(prompt_data, str) else "")
        prompt_files = getattr(prompt_data, "files", [])
        
        # If user uploads a file but types no text, prompt_text might be None.
        if prompt_text is None:
            prompt_text = ""
            
        docs_context = ""
        images = []
        
        if prompt_files:
            for file in prompt_files:
                filename = file.name.lower()
                if filename.endswith((".png", ".jpg", ".jpeg")):
                    file.seek(0)
                    base64_img = base64.b64encode(file.read()).decode('utf-8')
                    images.append(base64_img)
                else:
                    text = extract_text_from_file(file)
                    docs_context += f"--- Content of {file.name} ---\n{text}\n\n"
                    
        final_prompt = prompt_text
        if docs_context:
            final_prompt = f"Here are the attached documents for context:\n\n{docs_context}\nUser Question: {prompt_text}"
            
        # Build message
        user_msg = {"role": "user", "content": final_prompt}
        if images:
            user_msg["images"] = images
            
        st.session_state.messages.append(user_msg)
        
        with st.chat_message("user", avatar="👤"):
            if prompt_text:
                st.markdown(prompt_text)
            if docs_context:
                num_docs = sum(1 for f in prompt_files if not f.name.lower().endswith((".png", ".jpg", ".jpeg")))
                st.caption(f"📎 Attached {num_docs} document(s)")
            if images:
                st.caption(f"📎 Attached {len(images)} image(s)")
            
        # Setup assistant response
        with st.chat_message("assistant", avatar="🤖"):
            start_time = time.time()
            status = st.status("Thinking...", expanded=True)
            status.write("Understanding request...")
            time.sleep(0.2)
            if docs_context or images:
                status.write("Searching context...")
                time.sleep(0.2)
            status.write("Generating response...")
            
            response_placeholder = st.empty()
            full_response = ""
            
            # Setup generation parameters
            model = st.session_state.get("selected_model", "llama3")
            temperature = st.session_state.get("temperature", 0.7)
            max_tokens = st.session_state.get("max_tokens", 2048)
            
            # Pass messages to API
            api_messages = []
            for m in st.session_state.messages:
                msg_payload = {"role": m["role"], "content": m["content"]}
                if "images" in m and m["images"]:
                    msg_payload["images"] = m["images"]
                api_messages.append(msg_payload)
            
            try:
                def wrapped_stream():
                    first_chunk = False
                    for chunk in stream_chat(model, api_messages, temperature, max_tokens):
                        if not first_chunk:
                            first_chunk = True
                            # Collapse but keep loading spinner active
                            status.update(label="Generating response...", state="running", expanded=False)
                        yield chunk

                # Use Streamlit's native write_stream for the absolute best, smooth token fade-in animation
                full_response = st.write_stream(wrapped_stream())
                
                # Stream finished, mark complete
                elapsed = time.time() - start_time
                status.update(label=f"Thought for {elapsed:.1f}s", state="complete", expanded=False)
                    
            except Exception as e:
                status.update(label="Error occurred", state="error", expanded=True)
                st.error(f"Error during generation: {str(e)}")
                return
                    
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        # Save chat to local storage
        chat_data = {
            "id": st.session_state.current_chat_id,
            "title": st.session_state.get("current_chat_title", ""),
            "messages": st.session_state.messages
        }
        saved_chat = save_chat(chat_data)
        st.session_state.current_chat_title = saved_chat["title"]
        
        # Force a rerun to update sidebar history list
        st.rerun()
