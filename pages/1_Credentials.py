import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import load_env_file, write_env_file, ENV_FILE

st.title("Credentials")
st.caption(f"Editing: `{ENV_FILE}`")

current = load_env_file()

st.subheader("Preservica")
with st.form("credentials_form"):
    username = st.text_input("USERNAME", value=current.get("USERNAME", ""))
    password = st.text_input("PASSWORD", value=current.get("PASSWORD", ""), type="password")
    tenant   = st.text_input("TENANT",   value=current.get("TENANT", ""))
    server   = st.text_input("SERVER",   value=current.get("SERVER", ""),
                             help="e.g. us.preservica.com")
    submitted = st.form_submit_button("Save")

if submitted:
    write_env_file({
        "USERNAME": username,
        "PASSWORD": password,
        "TENANT": tenant,
        "SERVER": server,
    })
    st.success("Preservica credentials saved.")

st.subheader("Semaphore")
with st.form("semaphore_form"):
    api_key = st.text_input("SEMAPHORE_API_KEY", value=current.get("SEMAPHORE_API_KEY", ""), type="password")
    sem_submitted = st.form_submit_button("Save")

if sem_submitted:
    write_env_file({"SEMAPHORE_API_KEY": api_key})
    st.success("Semaphore credentials saved.")

st.divider()
st.caption("These credentials are stored in the repository `.env` file and loaded by all scripts via `python-dotenv`.")
