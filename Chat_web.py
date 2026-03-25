import streamlit as st
import pyrebase
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- 1. FIREBASE CONFIG ---
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

GROUP_PASSWORD = "@khul-ja-sim-sim" 

st.set_page_config(page_title="Krishna's Pro Chat", page_icon="🔥")
st_autorefresh(interval=3000, key="frefresher")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- 2. LOGIN ---
if not st.session_state.authenticated:
    st.title("🔐 Private Access")
    pwd = st.text_input("Password:", type="password")
    name = st.text_input("Apna Naam:")
    if st.button("Enter Chat"):
        if pwd == GROUP_PASSWORD and name:
            st.session_state.authenticated = True
            st.session_state.my_name = name
            st.rerun()
        else:
            st.error("Galti hai bhai!")

# --- 3. CHAT AREA ---
else:
    st.markdown(f"### 💬 Chatting as: {st.session_state.my_name}")
    
    try:
        msgs = db.child("messages").get().val()
        if msgs:
            for m_id in list(msgs.keys()):
                m = msgs[m_id]
                user = m.get('user', 'Unknown')
                text = m.get('msg', '')
                time = m.get('time', '')
                seen_list = m.get('seen_by', {}) # Kis kis ne dekha

                # Logic: Agar maine nahi dekha, toh mera naam add kar do
                if st.session_state.my_name not in seen_list:
                    db.child("messages").child(m_id).child("seen_by").update({st.session_state.my_name: True})

                # Seen users ke naam nikalna
                seen_names = ", ".join(seen_list.keys()) if seen_list else ""

                # Styling (Me vs Others)
                if user == st.session_state.my_name:
                    st.markdown(f"""
                        <div style='text-align: right; background-color: #DCF8C6; padding: 10px; border-radius: 15px; margin-bottom: 5px; margin-left: 20%; color: black;'>
                            <b>You</b><br>{text}<br>
                            <small style='color: gray; font-size: 10px;'>{time} | Seen by: {seen_names}</small>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style='text-align: left; background-color: #FFFFFF; padding: 10px; border-radius: 15px; margin-bottom: 5px; margin-right: 20%; color: black; border: 1px solid #ddd;'>
                            <b style='color: #075E54;'>{user}</b><br>{text}<br>
                            <small style='color: gray; font-size: 10px;'>{time} | Seen by: {seen_names}</small>
                        </div>
                    """, unsafe_allow_html=True)
    except:
        st.write("Messages load ho rahe hain...")

    # --- 4. INPUT ---
    prompt = st.chat_input("Message...")
    if prompt:
        now = datetime.now().strftime("%H:%M")
        db.child("messages").push({
            "user": st.session_state.my_name,
            "msg": prompt,
            "time": now,
            "seen_by": {st.session_state.my_name: True} # Bhejne wala toh dekh hi chuka hai
        })
        st.rerun()
