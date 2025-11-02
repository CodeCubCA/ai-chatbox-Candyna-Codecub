import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Music Advisor AI",
    page_icon="🎵",
    layout="wide"
)

# Initialize Groq client
def init_groq_client():
    """Initialize Groq API client"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("❌ Please set GROQ_API_KEY in your .env file")
        st.stop()
    return Groq(api_key=api_key)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add system prompt to define AI assistant role
    st.session_state.messages.append({
        "role": "system",
        "content": "You are a professional music advisor. You have deep knowledge of various music genres, artists, albums, and music history. You can recommend music based on users' moods, scenarios, or preferences, share music knowledge, and provide personalized music suggestions. Please communicate with users in a friendly and enthusiastic tone."
    })

# Create Groq client
client = init_groq_client()

# Page title and description
st.title("🎵 Music Advisor AI")
st.markdown("**Your Personal Music Recommendation Assistant** - Tell me your mood, scenario, or preferences, and I'll recommend the perfect music for you!")

# Add sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This is an AI-based music advisor assistant that can help you:
    - 🎧 Get music recommendations based on your mood
    - 🎼 Discover new artists and albums
    - 📚 Learn about music history and knowledge
    - 🎹 Receive personalized music suggestions
    """)

    st.header("🎯 Usage Tips")
    st.markdown("""
    Try these questions:
    - "Recommend some music for working"
    - "I'm feeling down, what songs should I listen to?"
    - "Tell me about the history of jazz"
    - "What are some classic rock albums?"
    """)

    # Clear conversation button
    if st.button("🗑️ Clear Chat History"):
        # Keep system prompt
        system_message = st.session_state.messages[0]
        st.session_state.messages = [system_message]
        st.rerun()

# Display chat history (don't show system prompt)
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Enter your question..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Call Groq API (streaming response)
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                temperature=0.7,
                max_tokens=2048,
                stream=True
            )

            # Display response word by word
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            # Display complete response
            message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"❌ Error occurred: {str(e)}")
            full_response = "Sorry, I encountered some issues. Please try again later."
            message_placeholder.markdown(full_response)

    # Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Powered by Groq API and Streamlit | Model: llama-3.3-70b-versatile"
    "</div>",
    unsafe_allow_html=True
)
