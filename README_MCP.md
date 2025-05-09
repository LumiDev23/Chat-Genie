# Advanced AI Chatbot with MCP Support

This chatbot application can connect to either an Anthropic Claude API or a local Model Control Protocol (MCP) server, giving you flexibility in how you use AI models.

## Installation

1. Install the required packages:
   ```bash
   pip install streamlit requests flask
   ```

2. If you want to use a local model with MCP, install the necessary libraries for your model. For example, for llama-cpp:
   ```bash
   pip install llama-cpp-python
   ```

## Setup

### For Claude API
1. Create a `.streamlit/secrets.toml` file with your Anthropic API key:
   ```toml
   ANTHROPIC_API_KEY = "your-anthropic-api-key"
   ```

### For MCP Server
1. Save the MCP server example script to a file (e.g., `mcp_server.py`)
2. Modify it to work with your preferred local model (example placeholders for llama-cpp are included)

## Running the Chatbot

### Basic Usage with Anthropic Claude API
```bash
streamlit run app.py
```

### With Local MCP Server

#### Start the MCP server
```bash
python mcp_server.py --port=5000 --model_path=/path/to/your/model.gguf
```

#### Start the Streamlit app with URL parameters for MCP
Visit the app in your browser with appropriate URL parameters:
```
http://localhost:8501/?mcp_script=mcp_server.py&mcp_port=5000
```

This will automatically connect the app to your running MCP server.

To force using Anthropic, add the `use_anthropic=true` parameter:
```
http://localhost:8501/?use_anthropic=true
```

## Features

- **Dual Backend Support**: Switch between Anthropic Claude API and local MCP server
- **Auto-connecting to MCP**: Can automatically connect to your MCP server
- **Model Selection**: Choose between different Claude models when using Anthropic
- **Clean UI**: Nice chat interface with typing animation
- **Secure**: API keys stored in Streamlit secrets, not exposed in the UI

## URL Parameters

- `mcp_script`: Path to the MCP server Python script (required for MCP mode)
- `mcp_port`: Port for the MCP server (default: 5000)
- `use_anthropic`: Set to `true` to use Anthropic API instead of MCP

## How the MCP Server Works

The MCP (Model Control Protocol) server provides an OpenAI-compatible API interface that can be used with any local language model. This means your local models can use the same API format as OpenAI's models, making it easy to switch between local and cloud-based AI.

The example MCP server includes:

1. A Flask web server that exposes endpoints compatible with OpenAI's API
2. Endpoints for `/v1/chat/completions` similar to OpenAI's format
3. A simple implementation that you can extend with your preferred model library

## Troubleshooting

- **Connection Issues**: If the chatbot can't connect to the MCP server, make sure the server is running and the port matches
- **API Key Issues**: For Claude, ensure your API key is correctly set in the secrets file
- **Black Screen**: If you see a black screen, try restarting both the server and the app
- **Model Loading Errors**: Check your model path and ensure you have enough memory to load the model

## Security Considerations

- Never commit your `.streamlit/secrets.toml` file to version control
- For deployments, use appropriate secrets management for the platform
- Be aware that the MCP server accepts incoming connections, so use appropriate network security

## Extending the App

Some ideas for extending this application:

1. Add authentication to the MCP server
2. Support multiple different local models
3. Implement file upload capabilities
4. Add chat history export
5. Implement memory management for longer conversations# Advanced AI Chatbot with MCP Support

This chatbot application can connect to either an Anthropic Claude API or a local Model Control Protocol (MCP) server, giving you flexibility in how you use AI models.

## Installation

1. Install the required packages:
   ```bash
   pip install streamlit requests flask
   ```

2. If you want to use a local model with MCP, install the necessary libraries for your model. For example, for llama-cpp:
   ```bash
   pip install llama-cpp-python
   ```

## Setup

### For Claude API
1. Create a `.streamlit/secrets.toml` file with your Anthropic API key:
   ```toml
   ANTHROPIC_API_KEY = "your-anthropic-api-key"
   ```

### For MCP Server
1. Save the MCP server example script to a file (e.g., `mcp_server.py`)
2. Modify it to work with your preferred local model (example placeholders for llama-cpp are included)

## Running the Chatbot

### With Anthropic Claude API
```bash
streamlit run app.py --use_anthropic
```

### With Local MCP Server
```bash
# First terminal: Start the MCP server
python mcp_server.py --port=5000 --model_path=/path/to/your/model.gguf

# Second terminal: Start the Streamlit app with MCP
streamlit run app.py --mcp_script=mcp_server.py --mcp_port=5000
```

## Features

- **Dual Backend Support**: Switch between Anthropic Claude API and local MCP server
- **Auto-starting MCP**: Can automatically start and manage your MCP server
- **Model Selection**: Choose between different Claude models when using Anthropic
- **Clean UI**: Nice chat interface with typing animation
- **Secure**: API keys stored in Streamlit secrets, not exposed in the UI

## Command Line Arguments

- `--mcp_script`: Path to the MCP server Python script (required for MCP mode)
- `--mcp_port`: Port for the MCP server (default: 5000)
- `--use_anthropic`: Use Anthropic API instead of MCP

## Troubleshooting

- If you see a black screen, try running with a simpler configuration first
- Check the browser console and terminal for error messages
- Make sure your API key is correctly set in the secrets file
- For MCP server issues, check if the port is available and not blocked by a firewall

## Security Considerations

- Never commit your `.streamlit/secrets.toml` file to version control
- For deployments, use appropriate secrets management for the platform
- Consider the security implications of allowing arbitrary MCP scripts to be executed