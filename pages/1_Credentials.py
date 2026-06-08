import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import (
    load_env_file, write_env_file, get_env_file,
    get_repo_root, get_semaphore_dir, save_paths_config, repos_present,
)

st.title("Credentials and Configuration")
st.caption(f"Editing: `{get_env_file()}`")

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

st.divider()
st.subheader("Project Folder Paths")
st.markdown("These paths tell the app where to find the required script repositories.")

presence = repos_present()

col1, col2 = st.columns(2)
with col1:
    if presence["main"]:
        st.success(f"**digital-archiving-scripts** found")
    else:
        st.error(f"**digital-archiving-scripts** not found")
with col2:
    if presence["semaphore"]:
        st.success(f"**semaphore-classification-python** found")
    else:
        st.warning(f"**semaphore-classification-python** not found *(optional)*")

with st.form("paths_form"):
    new_repo_root = st.text_input(
        "digital-archiving-scripts path",
        value=str(get_repo_root()),
    )
    new_semaphore_dir = st.text_input(
        "semaphore-classification-python path",
        value=str(get_semaphore_dir()),
    )
    paths_submitted = st.form_submit_button("Save paths")

if paths_submitted:
    save_paths_config({
        "repo_root": new_repo_root,
        "semaphore_dir": new_semaphore_dir,
    })
    st.success("Folder paths saved.")
    st.rerun()
