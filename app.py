import streamlit as st
from google import genai

# 🔑 Use Google API key 
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

st.set_page_config(page_title="PARKONIC AI ASSISTANT", page_icon="🤖", layout="wide")



st.markdown(

    f"""

    <style>

  

    /* Main container */

    .block-container {{

        padding-top: 2rem;

        max-width: 1000px;

    }}

    /* Header */

    .main-title {{

        text-align: center;

        color: #222;

        font-size: 42px;

        font-weight: bold;

        margin-bottom: 0px;

    }}

    .sub-title {{

        text-align: center;

        color: #555;

        margin-bottom: 30px;

    }}

   

    </style>

    """,

    unsafe_allow_html=True

)


# Header

st.markdown(

    """

    <div class="main-title">

        PARKONIC AI ASSISTANT

    </div>

    <div class="sub-title">

        Customer Support Chatbot

    </div>

    """,

    unsafe_allow_html=True

)

# Sidebar
with st.sidebar:
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
user_input = st.chat_input("As anything...")

if user_input:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Build conversation prompt for Gemini
    history = "\n".join(
        [f"{m['role']}: {m['content']}"
        for m in st.session_state.messages]
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
                contents=[prompt]
            )

            reply = response.text
            st.markdown(reply)

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": reply})
