import streamlit as st
import pyrebase
from streamlit_autorefresh import st_autorefresh

config = {
    "apiKey": "AIzaSyAAZkbhE679efiT5vZXYb7LzjAkiMCp0Oo",
    "authDomain": "pvchat-frinshipzone.firebaseapp.com",
    "databaseURL": "https://pvchat-frinshipzone-default-rtdb.firebaseio.com",
    "projectId": "pvchat-frinshipzone",
    "storageBucket": "pvchat-frinshipzone.firebasestorage.app",
    "messagingSenderId": "920799203773",
    "appId": "1:920799203773:web:f56cd425dc55a6196fc2d4"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

# Har 3 second mein refresh
st_autorefresh(interval=3000, key="frefresher")

st.title("💬 Krishna's Chat Board")

if "my_name" not in st.session_state:
    st.session_state.my_name = ""

if not st.session_state.my_name:
    n = st.text_input("Naam dalo:")
    if n:
        st.session_state.my_name = n
        st.rerun()
else:
    # --- MESSAGES LOAD KARO ---
    try:
        # ".get()" ke saath error handle karne ke liye
        msgs = db.child("messages").get().val()
        if msgs:
            for m_id in list(msgs.keys()):
                m = msgs[m_id]
                with st.chat_message("user"):
                    st.write(f"**{m['user']}**: {m['msg']}")
    except:
        st.warning("Database refresh ho raha hai... (Wait 2 sec)")

    # --- CHAT INPUT ---
    prompt = st.chat_input("Message...")
    if prompt:
        db.child("messages").push({"user": st.session_state.my_name, "msg": prompt})
        st.rerun()
