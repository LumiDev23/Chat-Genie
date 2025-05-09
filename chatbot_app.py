import streamlit as st
import random
import time

# Set page configuration
st.set_page_config(
    page_title="Enhanced Chatbot",
    page_icon="🤖",
    layout="centered"  # Using centered layout instead of wide for better compatibility
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
st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>🤖 Friendly Chat Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; margin-bottom: 30px;'>Ask me anything, share your thoughts, or just say hello!</p>", unsafe_allow_html=True)

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add a welcome message
    st.session_state.messages.append({"role": "assistant", "content": "Hello! I'm your friendly chat assistant. How can I help you today?"})

# Define enhanced chatbot responses
bot_responses = {
    "greeting": ["Hello there! How are you doing today?", "Hi! How can I help you today?", "Hey! Nice to meet you! What's on your mind?"],
    "how_are_you": ["I'm doing well, thanks for asking! How about you?", "I'm great! How has your day been so far?", "All systems operational and ready to chat! How are you feeling today?"],
    "goodbye": ["Goodbye! Have a wonderful day ahead!", "See you later! Come back anytime.", "Take care! Looking forward to our next conversation."],
    "thanks": ["You're welcome! Happy to help anytime.", "My pleasure! Is there anything else you'd like to know?", "Anytime! That's what I'm here for."],
    "weather": ["I don't have real-time weather data, but I'd be happy to chat about the weather! How's it looking outside your window?", "Weather can really affect our mood, don't you think? What's your favorite kind of weather?"],
    "joke": ["Why don't scientists trust atoms? Because they make up everything!", "How does a penguin build its house? Igloos it together!", "Why did the scarecrow win an award? Because he was outstanding in his field!"],
    "default": ["Interesting! Tell me more about that.", "I'm curious to hear more about your thoughts on this.", "That's fascinating! Would you like to elaborate?", "Thank you for sharing that with me. What else is on your mind?"]
}

# Function to determine the response category
def categorize_message(message):
    message = message.lower()
    
    if any(word in message for word in ["hello", "hi", "hey", "greetings"]):
        return "greeting"
    elif any(phrase in message for phrase in ["how are you", "how's it going", "how are things"]):
        return "how_are_you"
    elif any(word in message for word in ["bye", "goodbye", "see you", "farewell"]):
        return "goodbye"
    elif any(word in message for word in ["thanks", "thank you", "appreciate"]):
        return "thanks"
    elif any(word in message for word in ["weather", "rain", "sunny", "forecast"]):
        return "weather"
    elif any(word in message for word in ["joke", "funny", "laugh"]):
        return "joke"
    else:
        return "default"

# Function to get bot response
def get_bot_response(user_message):
    category = categorize_message(user_message)
    return random.choice(bot_responses[category])

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
    
    # Get bot response
    bot_response = get_bot_response(prompt)
    
    # Display bot response with typing animation
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        
        # Simulate typing with a gentler approach that won't cause rendering issues
        full_response = ""
        for chunk in bot_response.split():
            full_response += chunk + " "
            message_placeholder.write(full_response + "▌")
            time.sleep(0.05)  # Slightly slower for stability
            
        # Write the final response
        message_placeholder.write(bot_response)
    
    # Add bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

# Add a sidebar with information and controls
with st.sidebar:
    st.markdown("## About this Chatbot")
    st.markdown("""
    This enhanced chatbot demonstrates several Streamlit features:
    
    - Chat interface with history
    - Message categorization
    - Typing animation effect
    - Custom styling
    - Session state management
    
    Try asking about:
    - How it's doing
    - The weather
    - Tell a joke
    - Or just chat about anything!
    """)
    
    # Add a clear conversation button in the sidebar
    if st.button("Clear Conversation", key="clear_convo"):
        st.session_state.messages = []
        st.session_state.messages.append({"role": "assistant", "content": "Hello! I'm your friendly chat assistant. How can I help you today?"})
        st.rerun()
        
    # Add some credits
    st.markdown("---")
    st.markdown("Made with Streamlit ❤️")