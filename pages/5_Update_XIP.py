import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import credentials_sidebar, credentials_valid, run_script, save_uploaded_file

credentials_sidebar()
st.title("Update XIP")
st.caption("Update asset titles, descriptions and security tags from a CSV (`d_update_xip_from_csv.py`)")
st.info(
    "The CSV must have these columns: `assetId`, `entity.title`, `entity.description`, "
    "`asset.security_tag`, `entity.entity_type`."
)

if not credentials_valid():
    st.error("Credentials not configured. Go to the Credentials page first.")
    st.stop()

csv_file = st.file_uploader("CSV file", type=["csv"])

if st.button("Run", type="primary"):
    if not csv_file:
        st.error("Upload a CSV file.")
        st.stop()

    csv_path = save_uploaded_file(csv_file, ".csv")
    returncode, _ = run_script("update_xip", ["--csv-file", csv_path])

    if returncode == 0:
        st.success("Completed successfully.")
    else:
        st.error("Script exited with errors. See output above.")
