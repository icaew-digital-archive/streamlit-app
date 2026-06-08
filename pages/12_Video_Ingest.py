import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import credentials_sidebar, credentials_valid, run_script

credentials_sidebar()
st.title("Video Ingest")
st.caption("Upload video files and paired subtitle (.srt) files to Preservica (`video_subtitle_package_ingest.py`)")
st.info(
    "Looks for `.mp4`, `.mkv`, `.avi`, `.mov` and `.flv` files in the specified folder. "
    "If a matching `.srt` file exists it is included in the package."
)

if not credentials_valid():
    st.error("Credentials not configured. Go to the Credentials page first.")
    st.stop()

video_folder = st.text_input(
    "Video folder (local path)",
    placeholder="/path/to/videos",
    help="Folder on this machine containing the video (and optionally .srt) files",
)
preservica_folder_id = st.text_input(
    "Preservica destination folder ID",
    placeholder="UUID of the target folder in Preservica",
)

if st.button("Run", type="primary"):
    if not video_folder:
        st.error("Enter the video folder path.")
        st.stop()
    if not preservica_folder_id:
        st.error("Enter the Preservica folder ID.")
        st.stop()
    if not Path(video_folder).is_dir():
        st.error(f"Folder not found: {video_folder}")
        st.stop()

    returncode, _ = run_script(
        "video_ingest",
        ["--video_folder", video_folder, "--preservica_folder_id", preservica_folder_id],
    )

    if returncode == 0:
        st.success("Upload completed successfully.")
    else:
        st.error("Script exited with errors. See output above.")
