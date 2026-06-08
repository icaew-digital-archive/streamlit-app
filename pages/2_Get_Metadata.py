import tempfile
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import credentials_sidebar, credentials_valid, run_script, save_uploaded_file, save_text_as_file, get_repo_root

credentials_sidebar()
st.title("Get Metadata")
st.caption("Export metadata and checksums from Preservica to CSV (`a_get_metadata.py`)")

if not credentials_valid():
    st.error("Credentials not configured. Go to the Credentials page first.")
    st.stop()

st.subheader("Source")
source_type = st.radio(
    "Get entities from",
    ["Folder reference", "References (assets or folders)", "References file (assets or folders)"],
    horizontal=True,
)

folder_ref = ""
refs_file_path = None

if source_type == "Folder reference":
    folder_ref = st.text_input(
        "Folder reference",
        placeholder='e.g. bb45f999-7c07-4471-9c30-54b057c500ff  (or "root")',
    )

elif source_type == "References (assets or folders)":
    pasted = st.text_area(
        "References (one per line)",
        height=150,
        placeholder="bb45f999-7c07-4471-9c30-54b057c500ff\ncc56e888-8d18-5582-0d41-65c168d611ee",
    )

elif source_type == "References file (assets or folders)":
    refs_file = st.file_uploader("References file (one reference per line)", type=["txt"])
    if refs_file:
        refs_file_path = save_uploaded_file(refs_file, ".txt")

st.subheader("Output")
output_csv = st.text_input(
    "Output CSV filename", value="metadata_export.csv",
    help="Saved relative to the repository root",
)

st.subheader("Options")
col1, col2 = st.columns(2)
with col1:
    algorithm   = st.selectbox("Checksum algorithm", ["ALL", "MD5", "SHA1", "SHA256"])
    entity_type = st.selectbox("Entity type", ["both", "assets", "folders"])
with col2:
    new_template    = st.checkbox("New template (extended Dublin Core columns)")
    all_generations = st.checkbox("All generations (default: first generation only)")

exclude_folders = st.text_area(
    "Exclude folder references (one per line, folder mode only)",
    height=80,
    placeholder="uuid-1\nuuid-2",
)

if st.button("Run", type="primary"):
    args = []

    if source_type == "Folder reference":
        if not folder_ref:
            st.error("Enter a folder reference.")
            st.stop()
        args += ["--preservica-folder-ref", folder_ref]

    elif source_type == "References (assets or folders)":
        if not pasted.strip():
            st.error("Paste at least one reference.")
            st.stop()
        refs_file_path = save_text_as_file(pasted.strip(), ".txt")
        args += ["--references-file", refs_file_path]

    elif source_type == "References file (assets or folders)":
        if not refs_file_path:
            st.error("Upload a references file.")
            st.stop()
        args += ["--references-file", refs_file_path]

    args += ["--metadata-csv", output_csv, "--algorithm", algorithm, "--entity-type", entity_type]

    if new_template:
        args.append("--new-template")
    if all_generations:
        args.append("--all-generations")
    if exclude_folders.strip():
        refs = [r.strip() for r in exclude_folders.splitlines() if r.strip()]
        args += ["--exclude-folders"] + refs

    returncode, _ = run_script("get_metadata", args)

    if returncode == 0:
        st.success("Completed successfully.")
        output_path = Path(output_csv) if Path(output_csv).is_absolute() else get_repo_root() / output_csv
        if output_path.exists():
            st.download_button(
                "Download CSV",
                data=output_path.read_bytes(),
                file_name=output_path.name,
                mime="text/csv",
            )
        else:
            st.warning(f"Output file not found at `{output_path}`.")
    else:
        st.error("Script exited with errors. See output above.")
