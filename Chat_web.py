import streamlit as st
import pyrebase
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import base64
import time

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

GROUP_PASSWORD = "BhaiKiSarkar123" 

st.set_page_config(page_title="Krishna's Smart Chat", page_icon="🔔")
st_autorefresh(interval=3000, key="frefresher")

# Notification Sound Function
def play_notification():
    # Chota sa beep sound (Base64 format mein)
    audio_html = """
        <audio autoplay>
            <source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "last_msg_count" not in st.session_state:
    st.session_state.last_msg_count = 0

# --- LOGIN GATE ---
if not st.session_state.authenticated:
    st.title("🔐 Access Gate")
    pwd = st.text_input("Password:", type="password")
    name = st.text_input("Naam:")
    if st.button("Enter"):
        if pwd == GROUP_PASSWORD and name:
            st.session_state.authenticated = True
            st.session_state.my_name = name
            st.rerun()

# --- CHAT AREA ---
else:
    st.title("💬 Live Chat Board")
    
    with st.sidebar:
        st.header("📸 Snap & Settings")
        img_file = st.file_uploader("Snap bhejien", type=['jpg', 'png', 'jpeg'])
        if img_file and st.button("Send Snap"):
            bytes_data = img_file.getvalue()
            base_64 = base64.b64encode(bytes_data).decode()
            db.child("messages").push({
                "user": st.session_state.my_name,
                "msg": "📷 [SNAP]",
                "image": base_64,
                "time": datetime.now().strftime("%H:%M"),
                "seen_by": {st.session_state.my_name: True}
            })
            st.rerun()
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

    # --- MESSAGE LISTENING & NOTIFICATION ---
    try:
        msgs_data = db.child("messages").get().val()
        if msgs_data:
            current_count = len(msgs_data)
            
            # Agar koi naya message aaya hai (jo maine nahi bheja)
            if current_count > st.session_state.last_msg_count:
                last_msg_id = list(msgs_data.keys())[-1]
                if msgs_data[last_msg_id]['user'] != st.session_state.my_name:
                    play_notification() # Notification bajao!
                    st.toast(f"Naya message aaya hai: {msgs_data[last_msg_id]['user']} se!")
                st.session_state.last_msg_count = current_count

            for m_id in list(msgs_data.keys()):
                m = msgs_data[m_id]
                user, text, time_str = m.get('user'), m.get('msg'), m.get('time')
                seen_list = m.get('seen_by', {})

                if st.session_state.my_name not in seen_list:
                    db.child("messages").child(m_id).child("seen_by").update({st.session_state.my_name: True})

                align = "right" if user == st.session_state.my_name else "left"
                bg = "#DCF8C6" if user == st.session_state.my_name else "#FFFFFF"
                
                st.markdown(f"""
                    <div style='text-align: {align}; background-color: {bg}; padding: 10px; border-radius: 15px; margin-bottom: 5px; color: black; border: 1px solid #ddd;'>
                        <b>{user}</b>: {text}<br>
                        <small style='color: gray;'>{time_str} | Seen by: {', '.join(seen_list.keys())}</small>
                    </div>
                """, unsafe_allow_html=True)
                
                if m.get('image'):
                    if st.button(f"👁️ View Snap", key=m_id):
                        st.image(f"data:image/png;base64,{m['image']}")
    except:
        pass

    # --- INPUT ---
    prompt = st.chat_input("Likho bhai...")
    if prompt:
        db.child("messages").push({
            "user": st.session_state.my_name,
            "msg": prompt,
            "time": datetime.now().strftime("%H:%M"),
            "seen_by": {st.session_state.my_name: True}
        })
        st.rerun()
