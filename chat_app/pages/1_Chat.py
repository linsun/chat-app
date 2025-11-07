import streamlit as st
import requests
import os

# Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

def call_ollama(prompt: str, model: str = None) -> str:
    """Call Ollama API"""
    if model is None:
        model = OLLAMA_MODEL
    
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json().get("response", "No response from Ollama")
    except requests.exceptions.ConnectionError:
        return "❌ Error: Could not connect to Ollama. Make sure Ollama is running at " + OLLAMA_BASE_URL
    except Exception as e:
        return f"❌ Error calling Ollama: {str(e)}"

# UI
st.title("💬 Chat with Ollama")

# Navigation
st.markdown("""
**Navigation:** [🏠 Home](/) | [🎵 Vote](/Vote)
""")

# Sidebar
with st.sidebar:
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.success("Chat cleared!")
        st.rerun()

# Chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Type your message..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Process and generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Build conversation context
            conversation_context = ""
            for msg in st.session_state.messages[-5:]:  # Last 5 messages for context
                role = "User" if msg["role"] == "user" else "Assistant"
                conversation_context += f"{role}: {msg['content']}\n\n"
            
            # Add current user prompt
            full_prompt = conversation_context + f"User: {prompt}\n\nAssistant:"
            
            response = call_ollama(full_prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

