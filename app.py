import streamlit as st
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

# AI Provider Configuration
def get_available_providers():
    """Check which AI providers have API keys configured"""
    providers = {}

    if os.getenv("OPENAI_API_KEY"):
        providers["OpenAI"] = {
            "module": "openai",
            "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
        }

    if os.getenv("ANTHROPIC_API_KEY"):
        providers["Anthropic"] = {
            "module": "anthropic",
            "models": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"]
        }

    if os.getenv("GROQ_API_KEY"):
        providers["Groq"] = {
            "module": "groq",
            "models": ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "mixtral-8x7b-32768"]
        }

    return providers

def initialize_client(provider_name, api_key):
    """Initialize the appropriate AI client based on provider"""
    if provider_name == "OpenAI":
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    elif provider_name == "Anthropic":
        from anthropic import Anthropic
        return Anthropic(api_key=api_key)
    elif provider_name == "Groq":
        from groq import Groq
        return Groq(api_key=api_key)
    return None

def get_chat_response(client, provider_name, model, messages):
    """Get chat response based on provider"""
    if provider_name == "OpenAI":
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    elif provider_name == "Anthropic":
        # Anthropic uses different message format
        system_message = next((msg["content"] for msg in messages if msg["role"] == "system"), "")
        user_messages = [msg for msg in messages if msg["role"] != "system"]

        with client.messages.stream(
            model=model,
            max_tokens=2048,
            temperature=0.7,
            system=system_message,
            messages=user_messages
        ) as stream:
            for text in stream.text_stream:
                yield text

    elif provider_name == "Groq":
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add system prompt to define AI assistant role
    st.session_state.messages.append({
        "role": "system",
        "content": "You are a professional music advisor. You have deep knowledge of various music genres, artists, albums, and music history. You can recommend music based on users' moods, scenarios, or preferences, share music knowledge, and provide personalized music suggestions. Please communicate with users in a friendly and enthusiastic tone."
    })

# Page title and description
st.title("🎵 Music Advisor AI")
st.markdown("**Your Personal Music Recommendation Assistant** - Tell me your mood, scenario, or preferences, and I'll recommend the perfect music for you!")

# Get available providers
available_providers = get_available_providers()

# Add sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    if not available_providers:
        st.error("❌ No API keys found! Please set at least one API key in your .env file:")
        st.code("""OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GROQ_API_KEY=your_key_here""")
        st.stop()

    # Provider selection
    provider_name = st.selectbox(
        "AI Provider",
        options=list(available_providers.keys()),
        help="Select which AI provider to use"
    )

    # Model selection
    model = st.selectbox(
        "Model",
        options=available_providers[provider_name]["models"],
        help="Select which model to use"
    )

    st.markdown("---")

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
            # Get API key for selected provider
            api_key_map = {
                "OpenAI": "OPENAI_API_KEY",
                "Anthropic": "ANTHROPIC_API_KEY",
                "Groq": "GROQ_API_KEY"
            }
            api_key = os.getenv(api_key_map[provider_name])

            # Initialize client
            client = initialize_client(provider_name, api_key)

            # Get streaming response
            for chunk in get_chat_response(client, provider_name, model, st.session_state.messages):
                full_response += chunk
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
    f"<div style='text-align: center; color: #666;'>"
    f"Powered by {provider_name} and Streamlit | Model: {model}"
    "</div>",
    unsafe_allow_html=True
)
