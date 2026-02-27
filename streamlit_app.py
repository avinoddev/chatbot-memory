import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

st.title("Chatbot Memory UI")

email = st.text_input("Enter Email")

if st.button("Login / Create User"):
    res = requests.post(
        f"{BACKEND_URL}/users",
        json={"email": email}
    )

    data = res.json()

    st.session_state["user_id"] = data["user_id"]
    st.session_state["access_token"] = data["access_token"]
    st.json(data)

if "user_id" in st.session_state:
    st.subheader("User Info")

    user_res = requests.get(
        f"{BACKEND_URL}/users/{st.session_state['user_id']}"
    )

    st.json(user_res.json())

    if st.button("Create New Thread"):
        thread_res = requests.post(
            f"{BACKEND_URL}/threads",
            json={"user_id": st.session_state["user_id"]},
            headers={
                "Authorization": f"Bearer {st.session_state['access_token']}"
            }
        )
        st.session_state["thread_id"] = thread_res.json()["thread_id"]

    if "thread_id" in st.session_state:
        st.subheader("Chat")

        message = st.text_input("Message")

        if st.button("Send"):
            chat_res = requests.post(
                f"{BACKEND_URL}/messages",
                json={
                    "thread_id": st.session_state["thread_id"],
                    "role": "user",
                    "content": message
                },
                headers={
                    "Authorization": f"Bearer {st.session_state['access_token']}"
                }
            )

            st.write(chat_res.json()["response"])