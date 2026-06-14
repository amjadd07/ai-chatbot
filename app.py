import streamlit as st
from google import genai

# 🔑 Use Google API key 
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

st.set_page_config(page_title="AI Chatbot", page_icon="🤖")

# Sidebar
with st.sidebar:
    st.title("AI Chatbot")
    st.write("Customer Support Bot")

    if st.button("Clear Chat"):
        st.session_state.messages = []

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("💬 Chatbot")

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Type here...")

if user_input:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Build conversation prompt for Gemini
    history = "\n".join(
        [f"{m['role']}: {m['content']}" for m in st.session_state.messages]
    )

    prompt = f"""
You are a helpful assistant.

Conversation so far:
{history}

Assistant:
"""

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            reply = response.text
            st.markdown(reply)

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": reply})