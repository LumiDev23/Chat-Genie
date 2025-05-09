import streamlit as st
import requests
import json
import time
import os

# Set page configuration
st.set_page_config(
    page_title="Claude-Powered Chat Assistant",
    page_icon="🤖",
    layout="centered"
)

# Apply custom CSS for better styling
st.markdown("""
<style>
    .stChatFloatingInputContainer {
        border-top: 1px solid #ccc;
        padding-top: 10px;
    }
    .stChatMessage {
        padding: 10px;
    }
    .stButton button {
        width: 100%;
    }
    .stTitle {
        text-align: center;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Add a nice header
st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>🤖 Claude-Powered Chat Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; margin-bottom: 30px;'>Ask me anything! I'm powered by Anthropic's Claude AI.</p>", unsafe_allow_html=True)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add a welcome message
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Hello! I'm a chat assistant powered by Anthropic's Claude. How can I help you today?"
    })

# Function to call Claude API
def get_claude_response(messages):
    url = "https://api.anthropic.com/v1/messages"
    
    # Get API key from secrets
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except Exception as e:
        st.error("""
        Error: API key not found in secrets.
        
        To set up your API key:
        1. Create a file at .streamlit/secrets.toml in your project directory
        2. Add your API key: ANTHROPIC_API_KEY = "your-api-key-here"
        3. Restart the Streamlit app
        """)
        st.stop()
    
    # Convert Streamlit message format to Claude's format
    claude_messages = []
    for msg in messages[-10:]:  # Only use last 10 messages to keep context window reasonable
        if msg["role"] == "user":
            claude_messages.append({"role": "user", "content": msg["content"]})
        elif msg["role"] == "assistant":
            claude_messages.append({"role": "assistant", "content": msg["content"]})
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    payload = {
        "model": "claude-3-haiku-20240307",  # You can change this to other Claude models
        "max_tokens": 1000,
        "messages": claude_messages
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["content"][0]["text"]
    except Exception as e:
        st.error(f"Error calling Claude API: {str(e)}")
        if 'response' in locals() and hasattr(response, 'text'):
            st.error(f"Response error: {response.text}")
        return "I'm having trouble connecting to my AI backend. Please check the API key in your secrets file and try again."

# Sidebar with information
with st.sidebar:
    st.markdown("## About this Chatbot")
    
    st.markdown("""
    This enhanced chatbot is powered by Anthropic's Claude AI model. It can:
    
    - Answer questions on almost any topic
    - Help with writing and creative tasks
    - Provide explanations and insights
    - Engage in thoughtful conversation
    
    The API key is securely stored in the Streamlit secrets manager.
    """)
    
    # Model selector
    model_options = {
        "claude-3-haiku-20240307": "Claude 3 Haiku (Fast)",
        "claude-3-sonnet-20240229": "Claude 3 Sonnet (Balanced)",
        "claude-3-opus-20240229": "Claude 3 Opus (Powerful)"
    }
    
    selected_model = st.selectbox(
        "Select Claude model:",
        list(model_options.keys()),
        format_func=lambda x: model_options[x]
    )
    
    # Add a clear conversation button in the sidebar
    if st.button("Clear Conversation", key="clear_convo"):
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "Hello! I'm a chat assistant powered by Anthropic's Claude. How can I help you today?"
        })
        st.rerun()
        
    # Add some credits
    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit and Anthropic's Claude")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
        st.write(message["content"])

# User input with chat_input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat container
    with st.chat_message("user", avatar="🧑‍💻"):
        st.write(prompt)
    
    # Display a spinner while waiting for Claude's response
    with st.spinner("Thinking..."):
        # Get response from Claude API
        claude_response = get_claude_response(st.session_state.messages)
    
    # Display Claude's response with typing animation
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        
        # Simulate typing with a gentle approach
        full_response = ""
        # Split the response into words for smoother animation
        words = claude_response.split()
        for i in range(0, len(words), 3):  # Process 3 words at a time for efficiency
            chunk = " ".join(words[i:i+3])
            full_response += chunk + " "
            message_placeholder.write(full_response + "▌")
            time.sleep(0.05)
            
        # Write the final response
        message_placeholder.write(claude_response)
    
    # Add Claude's response to chat history
    st.session_state.messages.append({"role": "assistant", "content": claude_response})