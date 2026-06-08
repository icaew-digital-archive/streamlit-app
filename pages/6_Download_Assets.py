import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import credentials_sidebar, credentials_valid, run_script, save_uploaded_file, save_text_as_file

credentials_sidebar()
st.title("Download Assets")
st.caption("Download asset files from Preservica with fixity verification (`download_preservica_assets.py`)")

if not credentials_valid():
    st.error("Credentials not configured. Go to the Credentials page first.")
    st.stop()

st.subheader("Source")
source_type = st.radio(
    "Download from",
    ["Single folder", "Folders file", "Paste asset references", "Assets file", "Single asset"],
    horizontal=True,
)

source_value     = ""
source_file_path = None
pasted           = ""

if source_type == "Single folder":
    source_value = st.text_input("Folder reference", placeholder='UUID or "root"')

elif source_type == "Single asset":
    source_value = st.text_input("Asset reference", placeholder="UUID")

elif source_type == "Paste asset references":
    pasted = st.text_area(
        "Asset references (one per line)",
        height=150,
        placeholder="cc56e888-8d18-5582-0d41-65c168d611ee\n4e979854-e1f0-4d31-84ce-92fab3b1ad9e",
    )

elif source_type == "Folders file":
    f = st.file_uploader("Folders file (one folder reference per line)", type=["txt"])
    if f:
        source_file_path = save_uploaded_file(f, ".txt")

elif source_type == "Assets file":
    f = st.file_uploader("Assets file (one asset reference per line)", type=["txt"])
    if f:
        source_file_path = save_uploaded_file(f, ".txt")

st.subheader("Destination")
download_folder = st.text_input("Download folder (local path)", placeholder="/path/to/downloads")

st.subheader("Options")
col1, col2 = st.columns(2)
with col1:
    original_only = st.checkbox("Original files only (skip derivatives)")
    use_asset_ref = st.checkbox("Use asset reference as filename")
with col2:
    exclude_exts = st.text_input("Exclude extensions (space-separated)", placeholder="mp4 avi mov")
    log_dir      = st.text_input("Log directory (optional)")

if st.button("Run", type="primary"):
    if source_type in ("Single folder", "Single asset") and not source_value:
        st.error("Enter a reference.")
        st.stop()
    if source_type == "Paste asset references" and not pasted.strip():
        st.error("Paste at least one asset reference.")
        st.stop()
    if source_type in ("Folders file", "Assets file") and not source_file_path:
        st.error("Upload a file.")
        st.stop()
    if not download_folder:
        st.error("Enter a download folder path.")
        st.stop()

    args = [download_folder]

    if source_type == "Single folder":
        args += ["--folder", source_value]
    elif source_type == "Single asset":
        args += ["--asset", source_value]
    elif source_type == "Paste asset references":
        tmp_path = save_text_as_file(pasted.strip(), ".txt")
        args += ["--assets-file", tmp_path]
    elif source_type == "Folders file":
        args += ["--folders-file", source_file_path]
    elif source_type == "Assets file":
        args += ["--assets-file", source_file_path]

    if original_only:
        args.append("--original-only")
    if use_asset_ref:
        args.append("--use-asset-ref")
    if exclude_exts.strip():
        args += ["--exclude-extensions"] + exclude_exts.split()
    if log_dir:
        args += ["--log-dir", log_dir]

    returncode, _ = run_script("download", args)

    if returncode == 0:
        st.success("Download completed successfully.")
    else:
        st.error("Script exited with errors. See output above.")
