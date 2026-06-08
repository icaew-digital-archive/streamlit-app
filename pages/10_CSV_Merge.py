import tempfile
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import credentials_sidebar, run_script, save_uploaded_file

credentials_sidebar()
st.title("CSV Merge")
st.caption("Merge multiple CSV files on the `assetId` column (`csv_merge.py`)")
st.info(
    "Upload two or more CSV files. The **first** file is the master — all rows are kept. "
    "Subsequent files are left-joined onto it by `assetId`."
)

uploaded_files = st.file_uploader(
    "CSV files (select multiple — order matters)",
    type=["csv"],
    accept_multiple_files=True,
)

if uploaded_files:
    st.caption(f"Files in order: {', '.join(f.name for f in uploaded_files)}")

st.divider()

subject_merge = st.checkbox(
    "Subject merge mode",
    value=True,
    help=(
        "Strips dc:subject from the master CSV. "
        "File 2 is treated as AI-generated subjects (fallback). "
        "File 3 (if provided) is treated as Semaphore subjects (primary) — "
        "any row with no Semaphore subjects falls back to the AI subjects."
    ),
)

if subject_merge:
    n = len(uploaded_files) if uploaded_files else 0
    if n == 0:
        st.caption("Upload files to see subject merge assignments.")
    else:
        lines = [f"- **File 1** ({uploaded_files[0].name}): master — dc:subject columns stripped"]
        if n > 1:
            lines.append(f"- **File 2** ({uploaded_files[1].name}): AI subjects (fallback)")
        if n > 2:
            lines.append(f"- **File 3** ({uploaded_files[2].name}): Semaphore subjects (primary)")
        st.markdown("\n".join(lines))

st.divider()

if st.button("Run", type="primary"):
    if len(uploaded_files) < 2:
        st.error("Upload at least two CSV files.")
        st.stop()

    temp_paths = [save_uploaded_file(f, ".csv") for f in uploaded_files]

    out_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    out_file.close()
    out_path = out_file.name

    extra_args = [] if subject_merge else ["--no-subject-merge"]
    returncode, _ = run_script("csv_merge", temp_paths + ["--output", out_path] + extra_args)

    if returncode == 0:
        csv_bytes = Path(out_path).read_bytes()
        st.success("Merge complete.")
        st.download_button(
            "Download merged CSV",
            data=csv_bytes,
            file_name="merged_output.csv",
            mime="text/csv",
        )
    else:
        st.error("Script exited with errors. See output above.")
