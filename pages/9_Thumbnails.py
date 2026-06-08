import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import credentials_sidebar, credentials_valid, run_script, save_uploaded_file

credentials_sidebar()
st.title("Thumbnails")
st.caption("Add, remove or download thumbnails for Preservica assets and folders (`remove_thumbnails.py`)")

if not credentials_valid():
    st.error("Credentials not configured. Go to the Credentials page first.")
    st.stop()

action = st.radio("Action", ["add", "remove", "download"], horizontal=True)

st.subheader("Target")
target_type = st.radio("Specify targets as", ["Single reference", "References file"], horizontal=True)

reference = ""
refs_file_path = None

if target_type == "Single reference":
    reference = st.text_input("Preservica reference (asset or folder UUID)")
else:
    refs_file = st.file_uploader("References file (one reference per line)", type=["txt"])
    if refs_file:
        refs_file_path = save_uploaded_file(refs_file, ".txt")

# Action-specific inputs
image_path = None
size = None

if action == "add":
    image_file = st.file_uploader("Thumbnail image", type=["jpg", "jpeg", "png", "gif"])
    if image_file:
        image_path = save_uploaded_file(image_file, Path(image_file.name).suffix)

elif action == "download":
    size = st.selectbox("Size", ["(default)", "LARGE", "MEDIUM", "SMALL"])
    if size == "(default)":
        size = None

if st.button("Run", type="primary"):
    if target_type == "Single reference" and not reference:
        st.error("Enter a reference.")
        st.stop()
    if target_type == "References file" and not refs_file_path:
        st.error("Upload a references file.")
        st.stop()
    if action == "add" and not image_path:
        st.error("Upload a thumbnail image.")
        st.stop()

    args = [action]

    if target_type == "Single reference":
        if action == "add":
            args += [reference, image_path]
        else:
            args.append(reference)
    else:
        if action == "add":
            args += [image_path, "--file", refs_file_path]
        else:
            args += ["--file", refs_file_path]

    if action == "download" and size:
        args += ["--size", size]

    returncode, _ = run_script("thumbnails", args)

    if returncode == 0:
        st.success("Completed successfully.")
    else:
        st.error("Script exited with errors. See output above.")
