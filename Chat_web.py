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

st.set_page_config(page_title="Krishna's Smart Chat", page_icon="🔔")
st_autorefresh(interval=3000, key="frefresher")

# --- CUSTOM JS FOR NOTIFICATION ---
# Ye script browser ko bolegi ki alert dikhaye
def notify_user(sender):
    js = f"""
    <script>
    if (window.Notification && Notification.permission === 'granted') {{
        new Notification('Naya Message!', {{ body: '{sender} ne message bheja hai' }});
    }} else if (window.Notification && Notification.permission !== 'denied') {{
        Notification.requestPermission();
    }}
    </script>
    """
    st.components.v1.html(js, height=0)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "old_msgs" not in st.session_state:
    st.session_state.old_msgs = []

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
    st.title("💬 Chat Board")
    
    # Message detection logic
    try:
        all_msgs = db.child("messages").get().val()
        if all_msgs:
            msg_ids = list(all_msgs.keys())
            
            # Agar last message id badal gayi hai aur wo maine nahi bheja
            if "last_id" not in st.session_state:
                st.session_state.last_id = msg_ids[-1]
            
            if msg_ids[-1] != st.session_state.last_id:
                latest_msg = all_msgs[msg_ids[-1]]
                if latest_msg['user'] != st.session_state.my_name:
                    # Notification trigger!
                    st.toast(f"🔔 {latest_msg['user']}: {latest_msg['msg']}")
                    notify_user(latest_msg['user'])
                st.session_state.last_id = msg_ids[-1]

            # Display Messages
            for m_id in msg_ids:
                m = all_msgs[m_id]
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
