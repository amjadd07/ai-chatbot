import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="AI Chatbot", page_icon="🤖")

# Sidebar
with st.sidebar:
    st.title("AI Chatbot")
    st.write("Customer Support Bot")
    if st.button("Clear Chat"):
        st.session_state.messages = []

# Chat memory
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("💬 Chatbot")

# show history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# input
user_input = st.chat_input("Type here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant"},
                    *st.session_state.messages
                ]
            )

            reply = response.choices[0].message.content
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})