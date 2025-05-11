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
    .sidebar-section {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    /* Server selector styling */
    .server-selector {
        margin-bottom: 10px;
    }
    /* Server configuration expander */
    .server-config {
        background-color: #f9f9f9;
        border-radius: 4px;
        padding: 8px;
        margin-bottom: 10px;
    }
    /* Status indicator */
    .status-indicator {
        text-align: right;
        font-size: 0.8em;
        color: #666;
        margin-bottom: 10px;
    }
    /* Server status indicator */
    .server-status {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 5px;
    }
    .server-status-active {
        background-color: #28a745;
    }
    .server-status-inactive {
        background-color: #dc3545;
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

if "run_mode" not in st.session_state:
    st.session_state.run_mode = "standalone"

# Function to call Claude API
def get_claude_response(messages, run_mode="standalone"):
    if run_mode == "standalone":
        return get_claude_direct(messages)
    else:
        return get_claude_via_mcp(messages)

def get_claude_direct(messages):
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
        "model": st.session_state.selected_model,
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

def get_claude_via_mcp(messages):
    # Get selected MCP server configuration
    if not st.session_state.mcp_servers or st.session_state.selected_mcp_server_index >= len(st.session_state.mcp_servers):
        st.error("MCP server configuration is missing or invalid.")
        st.stop()
        
    selected_server = st.session_state.mcp_servers[st.session_state.selected_mcp_server_index]
    mcp_endpoint = selected_server["endpoint"]
    #mcp_api_key = selected_server["api_key"]
    
    # Validate configuration
    #if not mcp_endpoint or not mcp_api_key:
    if not mcp_endpoint:
        st.error(f"""
        Error: MCP configuration for '{selected_server['name']}' is incomplete.
        
        Please provide both the API Endpoint and API Key in the server configuration.
        """)
        st.stop()
    
    # Convert Streamlit message format to MCP format
    mcp_payload = {
        "model": st.session_state.selected_model,
        "messages": [],
        "max_tokens": 1000,
        "project_id": st.session_state.mcp_project_id,
        "stream": False
    }
    
    for msg in messages[-10:]:
        if msg["role"] in ["user", "assistant"]:
            mcp_payload["messages"].append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    headers = {
        "Content-Type": "application/json"#,
        #"Authorization": f"Bearer {mcp_api_key}"
    }
    
    try:
        # Log server connection attempt (can be removed in production)
        st.session_state.last_used_server = selected_server["name"]
        
        # Make API request
        response = requests.post(mcp_endpoint, headers=headers, json=mcp_payload)
        response.raise_for_status()
        response_data = response.json()
        
        # Handle MCP-specific response format
        if "response" in response_data and "content" in response_data["response"]:
            return response_data["response"]["content"]
        else:
            return response_data.get("message", "Received an unexpected response format from MCP")
    except requests.exceptions.ConnectionError:
        st.error(f"Connection error: Could not connect to MCP server '{selected_server['name']}'. Please check the endpoint URL.")
        return f"I'm having trouble connecting to the MCP server '{selected_server['name']}'. Please check your endpoint URL and network connection."
    except requests.exceptions.Timeout:
        st.error(f"Timeout error: The request to MCP server '{selected_server['name']}' timed out.")
        return f"The request to MCP server '{selected_server['name']}' timed out. The server might be overloaded or experiencing issues."
    except requests.exceptions.HTTPError as http_err:
        status_code = http_err.response.status_code if hasattr(http_err, 'response') and hasattr(http_err.response, 'status_code') else "unknown"
        st.error(f"HTTP error: {status_code} when calling MCP server '{selected_server['name']}'.")
        
        if status_code == 401 or status_code == 403:
            return f"Authentication error when calling MCP server '{selected_server['name']}'. Please check your API key."
        else:
            return f"HTTP error {status_code} when calling MCP server '{selected_server['name']}'. Please check your configuration."
    except Exception as e:
        st.error(f"Error calling MCP API on server '{selected_server['name']}': {str(e)}")
        if 'response' in locals() and hasattr(response, 'text'):
            st.error(f"Response error: {response.text}")
        return f"I'm having trouble connecting to the MCP server '{selected_server['name']}'. Please check your MCP configuration and try again."

# Initialize tracking for last used server info
if "last_used_server" not in st.session_state:
    st.session_state.last_used_server = None

# Sidebar with information and settings
with st.sidebar:
    st.markdown("## Configuration")
    
    # Run mode selector (MCP or Standalone)
    run_mode_options = {
        "standalone": "Standalone (Direct API)",
        "mcp": "Mission Control Panel (MCP)"
    }
    
    st.session_state.run_mode = st.selectbox(
        "Run Mode:",
        list(run_mode_options.keys()),
        format_func=lambda x: run_mode_options[x],
        index=list(run_mode_options.keys()).index(st.session_state.get("run_mode", "standalone"))
    )
    
    # Conditional MCP settings
    if st.session_state.run_mode == "mcp":
        st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
        st.markdown("### MCP Settings")
        
        # Initialize MCP settings in session state if not exist
        if "mcp_servers" not in st.session_state:
            # Default to empty list or load from secrets if available
            try:
                # Try to load predefined servers from secrets
                mcp_servers_config = st.secrets.get("MCP_SERVERS", {})
                st.session_state.mcp_servers = []
                
                # Convert dict config to list for dropdown
                for name, config in mcp_servers_config.items():
                    st.session_state.mcp_servers.append({
                        "name": name,
                        "endpoint": config.get("endpoint", ""),
                        "api_key": config.get("api_key", ""),
                    })
                
                # If no predefined servers, add an empty default
                if not st.session_state.mcp_servers:
                    st.session_state.mcp_servers = [{
                        "name": "Default MCP",
                        "endpoint": "",
                        "api_key": "",
                    }]
            except Exception:
                # Fallback to a single default entry
                st.session_state.mcp_servers = [{
                    "name": "Default MCP",
                    "endpoint": "",
                    "api_key": "",
                }]
                
        if "selected_mcp_server_index" not in st.session_state:
            st.session_state.selected_mcp_server_index = 0
            
        if "mcp_project_id" not in st.session_state:
            st.session_state.mcp_project_id = ""
        
        # Server selection and management
        col1, col2 = st.columns([3, 1])
        
        with col1:
            server_names = [server["name"] for server in st.session_state.mcp_servers]
            st.session_state.selected_mcp_server_index = st.selectbox(
                "MCP Server:",
                range(len(server_names)),
                format_func=lambda i: server_names[i],
                index=st.session_state.selected_mcp_server_index
            )
        
        with col2:
            if st.button("Add Server", key="add_mcp_server"):
                # Add a new server configuration
                st.session_state.mcp_servers.append({
                    "name": f"MCP Server {len(st.session_state.mcp_servers) + 1}",
                    "endpoint": "",
                    "api_key": "",
                })
                # Select the new server
                st.session_state.selected_mcp_server_index = len(st.session_state.mcp_servers) - 1
                st.rerun()
        
        # Get the currently selected server
        selected_server = st.session_state.mcp_servers[st.session_state.selected_mcp_server_index]
        
        # Edit the selected server configuration
        with st.expander("Server Configuration", expanded=True):
            # Server name
            new_name = st.text_input(
                "Server Name:",
                value=selected_server["name"],
                key=f"server_name_{st.session_state.selected_mcp_server_index}"
            )
            st.session_state.mcp_servers[st.session_state.selected_mcp_server_index]["name"] = new_name
            
            # Server endpoint
            new_endpoint = st.text_input(
                "API Endpoint:",
                value=selected_server["endpoint"],
                key=f"server_endpoint_{st.session_state.selected_mcp_server_index}"
            )
            st.session_state.mcp_servers[st.session_state.selected_mcp_server_index]["endpoint"] = new_endpoint
            
            # Server API key
            new_api_key = st.text_input(
                "API Key:",
                value=selected_server["api_key"],
                type="password",
                key=f"server_api_key_{st.session_state.selected_mcp_server_index}"
            )
            st.session_state.mcp_servers[st.session_state.selected_mcp_server_index]["endpoint"] = new_endpoint
            st.session_state.mcp_servers[st.session_state.selected_mcp_server_index]["api_key"] = new_api_key
            
            # Delete button (don't allow deleting the last server)
            if len(st.session_state.mcp_servers) > 1:
                if st.button("Delete Server", key=f"delete_server_{st.session_state.selected_mcp_server_index}"):
                    st.session_state.mcp_servers.pop(st.session_state.selected_mcp_server_index)
                    st.session_state.selected_mcp_server_index = 0
                    st.rerun()
        
        # Project ID setting (applies to any server)
        st.session_state.mcp_project_id = st.text_input(
            "MCP Project ID:",
            value=st.session_state.mcp_project_id
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("### Model Settings")
    
    # Model selector
    model_options = {
        "claude-3-haiku-20240307": "Claude 3 Haiku (Fast)",
        "claude-3-sonnet-20240229": "Claude 3 Sonnet (Balanced)",
        "claude-3-opus-20240229": "Claude 3 Opus (Powerful)"
    }
    
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "claude-3-haiku-20240307"
        
    st.session_state.selected_model = st.selectbox(
        "Select Claude model:",
        list(model_options.keys()),
        format_func=lambda x: model_options[x],
        index=list(model_options.keys()).index(st.session_state.get("selected_model", "claude-3-haiku-20240307"))
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("## About this Chatbot")
    
    st.markdown("""
    This enhanced chatbot is powered by Anthropic's Claude AI model. It can:
    
    - Answer questions on almost any topic
    - Help with writing and creative tasks
    - Provide explanations and insights
    - Engage in thoughtful conversation
    
    The chatbot can be run in two modes:
    - **Standalone**: Directly calls Claude API
    - **MCP**: Routes through Mission Control Panel for enterprise features
    """)
    st.markdown("</div>", unsafe_allow_html=True)
    
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

# Status indicator for current mode
if st.session_state.run_mode == "standalone":
    status_text = f"Currently running in <strong>{run_mode_options[st.session_state.run_mode]}</strong> mode"
else:
    server_name = "Unknown"
    if "mcp_servers" in st.session_state and "selected_mcp_server_index" in st.session_state:
        if st.session_state.selected_mcp_server_index < len(st.session_state.mcp_servers):
            server_name = st.session_state.mcp_servers[st.session_state.selected_mcp_server_index]["name"]
    
    status_text = f"Currently running in <strong>{run_mode_options[st.session_state.run_mode]}</strong> mode via <strong>{server_name}</strong>"
    
    # Add last used server info if available and different from current
    if (st.session_state.last_used_server is not None and 
        st.session_state.last_used_server != server_name):
        status_text += f" (Last response from: <strong>{st.session_state.last_used_server}</strong>)"

st.markdown(
    f"<div style='text-align: right; font-size: 0.8em; color: #888;'>{status_text}</div>",
    unsafe_allow_html=True
)

# User input with chat_input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat container
    with st.chat_message("user", avatar="🧑‍💻"):
        st.write(prompt)
    
    # Display a spinner while waiting for Claude's response
    with st.spinner(f"Thinking... (via {run_mode_options[st.session_state.run_mode]})"):
        # Get response from Claude API
        claude_response = get_claude_response(st.session_state.messages, st.session_state.run_mode)
    
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