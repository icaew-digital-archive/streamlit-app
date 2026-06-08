import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import (
    credentials_sidebar, credentials_valid, run_script,
    save_uploaded_file, save_refs_as_csv,
)

credentials_sidebar()
st.title("Delete Metadata")
st.caption("Remove DC and ICAEW metadata schemas from assets or folders (`b_delete_metadata.py`)")

if not credentials_valid():
    st.error("Credentials not configured. Go to the Credentials page first.")
    st.stop()

st.warning("This operation **permanently removes metadata** from Preservica entities and cannot be undone.")

source_type = st.radio(
    "Delete metadata for entities from",
    ["References (assets or folders)", "CSV file", "Folder reference"],
    horizontal=True,
)

csv_path   = None
folder_ref = ""
pasted     = ""

if source_type == "References (assets or folders)":
    pasted = st.text_area(
        "Asset / folder references (one per line)",
        height=150,
        placeholder="bb45f999-7c07-4471-9c30-54b057c500ff\ncc56e888-8d18-5582-0d41-65c168d611ee",
    )

elif source_type == "CSV file":
    csv_file = st.file_uploader("CSV file (must have an `assetId` column)", type=["csv"])
    if csv_file:
        csv_path = save_uploaded_file(csv_file, ".csv")

elif source_type == "Folder reference":
    folder_ref = st.text_input(
        "Preservica folder reference",
        help="Metadata will be deleted from all descendants of this folder",
    )

log_dir = st.text_input("Log directory (optional)", placeholder="Leave blank for default")

# ── Step 1: Preview ──────────────────────────────────────────────────────────

if st.button("Preview entities to be affected"):
    if source_type == "References (assets or folders)":
        if not pasted.strip():
            st.error("Paste at least one reference.")
            st.stop()
        csv_path = save_refs_as_csv(pasted)
        st.session_state["delete_args"] = ["--csv-file", csv_path]

    elif source_type == "CSV file":
        if not csv_path:
            st.error("Upload a CSV file.")
            st.stop()
        st.session_state["delete_args"] = ["--csv-file", csv_path]

    elif source_type == "Folder reference":
        if not folder_ref:
            st.error("Enter a folder reference.")
            st.stop()
        st.session_state["delete_args"] = ["--preservica-folder-ref", folder_ref]

    if log_dir:
        st.session_state["delete_args"] += ["--log-dir", log_dir]

    _, preview_output = run_script(
        "delete_metadata", st.session_state["delete_args"], stdin_input="n\n"
    )
    st.session_state["delete_preview"] = preview_output

# ── Step 2: Show preview + confirm ───────────────────────────────────────────

if st.session_state.get("delete_preview"):
    st.subheader("Entities that will be affected")
    # Extract just the table section from the output for clarity
    output = st.session_state["delete_preview"]
    table_start = output.find("The following entities")
    table_end   = output.rfind("-" * 20)
    if table_start != -1 and table_end != -1:
        st.code(output[table_start : table_end + 80].strip(), language=None)
    else:
        st.code(output, language=None)

    confirmed = st.checkbox(
        "I confirm I want to permanently delete metadata from the entities listed above"
    )

    if st.button("Delete", type="primary", disabled=not confirmed):
        returncode, _ = run_script(
            "delete_metadata", st.session_state["delete_args"] + ["--yes"]
        )
        if returncode == 0:
            st.success("Metadata deleted successfully.")
            del st.session_state["delete_preview"]
            del st.session_state["delete_args"]
        else:
            st.error("Script exited with errors. See output above.")
