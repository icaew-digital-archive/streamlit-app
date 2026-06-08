import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import credentials_sidebar, credentials_valid, run_script, save_uploaded_file, save_text_as_file

credentials_sidebar()
st.title("Move Assets")
st.caption("Move assets or folders to a destination folder (`move_preservica_assets.py`)")

if not credentials_valid():
    st.error("Credentials not configured. Go to the Credentials page first.")
    st.stop()

source_type = st.radio(
    "Move",
    ["Paste asset references", "Assets file", "Single asset",
     "Paste folder references", "Folders file", "Single folder"],
    horizontal=True,
)

source_value     = ""
source_file_path = None
pasted           = ""

if source_type == "Single asset":
    source_value = st.text_input("Asset reference", placeholder="UUID")

elif source_type == "Single folder":
    source_value = st.text_input("Folder reference", placeholder="UUID")

elif source_type in ("Paste asset references", "Paste folder references"):
    label = "Asset references" if "asset" in source_type else "Folder references"
    pasted = st.text_area(
        f"{label} (one per line)",
        height=150,
        placeholder="cc56e888-8d18-5582-0d41-65c168d611ee\n4e979854-e1f0-4d31-84ce-92fab3b1ad9e",
    )

elif source_type == "Assets file":
    f = st.file_uploader("Assets file (one reference per line)", type=["txt"])
    if f:
        source_file_path = save_uploaded_file(f, ".txt")

elif source_type == "Folders file":
    f = st.file_uploader("Folders file (one reference per line)", type=["txt"])
    if f:
        source_file_path = save_uploaded_file(f, ".txt")

destination = st.text_input("Destination folder reference", placeholder="UUID")
log_dir     = st.text_input("Log directory (optional)")

confirmed = st.checkbox("I confirm I want to move these items")

if st.button("Run", type="primary", disabled=not confirmed):
    if source_type in ("Single asset", "Single folder") and not source_value:
        st.error("Enter a reference.")
        st.stop()
    if "Paste" in source_type and not pasted.strip():
        st.error("Paste at least one reference.")
        st.stop()
    if source_type in ("Assets file", "Folders file") and not source_file_path:
        st.error("Upload a file.")
        st.stop()
    if not destination:
        st.error("Enter a destination folder reference.")
        st.stop()

    args = ["--destination", destination, "--force"]

    if source_type == "Single asset":
        args += ["--asset", source_value]
    elif source_type == "Single folder":
        args += ["--folder", source_value]
    elif source_type == "Paste asset references":
        tmp_path = save_text_as_file(pasted.strip(), ".txt")
        args += ["--assets-file", tmp_path]
    elif source_type == "Paste folder references":
        tmp_path = save_text_as_file(pasted.strip(), ".txt")
        args += ["--folders-file", tmp_path]
    elif source_type == "Assets file":
        args += ["--assets-file", source_file_path]
    elif source_type == "Folders file":
        args += ["--folders-file", source_file_path]

    if log_dir:
        args += ["--log-dir", log_dir]

    returncode, _ = run_script("move", args)

    if returncode == 0:
        st.success("Move completed successfully.")
    else:
        st.error("Script exited with errors. See output above.")
