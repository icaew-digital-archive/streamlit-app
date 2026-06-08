import os
import tempfile
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import credentials_sidebar, run_script, save_uploaded_file, save_text_as_file

credentials_sidebar()
st.title("Semaphore Classification")
st.caption("Classify files using the Semaphore Classification Service (`semaphore_helper.py`)")

# ── File source ───────────────────────────────────────────────────────────────
st.subheader("Files to classify")
source_type = st.radio(
    "Source",
    ["Local directory", "Upload files", "Preservica folder", "Preservica asset references"],
    horizontal=True,
)

directory_path  = ""
upload_dir      = None
pasted_refs     = ""
preservica_arg  = None

if source_type == "Local directory":
    directory_path = st.text_input("Directory path", placeholder="/path/to/files")

elif source_type == "Upload files":
    uploaded = st.file_uploader(
        "Files to classify", accept_multiple_files=True,
        help="Files are saved to a temporary directory for processing",
    )
    if uploaded:
        upload_dir = tempfile.mkdtemp()
        for f in uploaded:
            (Path(upload_dir) / f.name).write_bytes(f.getvalue())
        st.caption(f"{len(uploaded)} file(s) ready in temp directory")

elif source_type == "Preservica folder":
    folder_ref = st.text_input("Preservica folder reference", placeholder="UUID")
    if folder_ref:
        preservica_arg = ("--preservica-folder-ref", folder_ref)

elif source_type == "Preservica asset references":
    pasted_refs = st.text_area(
        "Asset references (one per line)",
        height=120,
        placeholder="cc56e888-8d18-5582-0d41-65c168d611ee\n4e979854-e1f0-4d31-84ce-92fab3b1ad9e",
    )

# ── Classification options ────────────────────────────────────────────────────
st.subheader("Options")
col1, col2, col3 = st.columns(3)
with col1:
    threshold   = st.slider("Confidence threshold", 1, 99, 48)
    max_topics  = st.number_input("Max topics per file", min_value=1, max_value=50, value=10)
with col2:
    recursive       = st.checkbox("Recursive (include subdirectories)")
    include_scoring = st.checkbox("Include confidence scores in output")
with col3:
    keep_files      = st.checkbox(
        "Keep downloaded files",
        help="Only relevant when downloading from Preservica",
    )

col4, col5 = st.columns(2)
with col4:
    include_exts = st.text_input("Only process extensions (space-separated)", placeholder="pdf txt docx")
with col5:
    exclude_exts = st.text_input("Exclude extensions (space-separated)", placeholder="mp4 avi mov")

# ── Run ───────────────────────────────────────────────────────────────────────
if st.button("Run", type="primary"):
    # Determine working directory for files
    if source_type == "Local directory":
        if not directory_path:
            st.error("Enter a directory path.")
            st.stop()
        work_dir = directory_path
    elif source_type == "Upload files":
        if not upload_dir:
            st.error("Upload at least one file.")
            st.stop()
        work_dir = upload_dir
    elif source_type == "Preservica folder":
        if not folder_ref:
            st.error("Enter a folder reference.")
            st.stop()
        work_dir = tempfile.mkdtemp()
    elif source_type == "Preservica asset references":
        if not pasted_refs.strip():
            st.error("Paste at least one asset reference.")
            st.stop()
        work_dir = tempfile.mkdtemp()

    out_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    out_file.close()
    out_path = out_file.name

    args = [
        work_dir,
        "--threshold", str(threshold),
        "--max-topics", str(max_topics),
        "--csv", out_path,
    ]

    if recursive:
        args.append("--recursive")
    if include_scoring:
        args.append("--include-scoring")
    if keep_files:
        args.append("--keep-files")
    if include_exts.strip():
        args += ["--include-extensions"] + include_exts.split()
    if exclude_exts.strip():
        args += ["--exclude-extensions"] + exclude_exts.split()

    # Preservica source args
    if source_type == "Preservica folder" and folder_ref:
        args += ["--preservica-folder-ref", folder_ref]
    elif source_type == "Preservica asset references":
        refs_file = save_text_as_file(pasted_refs.strip(), ".txt")
        args += ["--preservica-assets-file", refs_file]

    returncode, _ = run_script("semaphore", args)

    if returncode == 0:
        try:
            df = pd.read_csv(out_path)
            st.success(f"Classified {len(df)} file(s).")
            st.dataframe(df, width='stretch')
            st.download_button(
                "Download CSV",
                data=Path(out_path).read_bytes(),
                file_name="semaphore_classifications.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.warning(f"Script completed but could not read CSV output: {e}")
    else:
        st.error("Script exited with errors. See output above.")
