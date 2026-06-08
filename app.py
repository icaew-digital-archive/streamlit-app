import subprocess
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    get_repo_root, get_semaphore_dir, save_paths_config,
    repos_present, REPO_URLS,
)

st.set_page_config(
    page_title="Digital Archiving Tools",
    page_icon="🗄",
    layout="wide",
)

st.markdown("""
<style>
[data-testid="stSidebarNavItems"] {
    max-height: none !important;
    overflow-y: visible !important;
}
[data-testid="stSidebarNavViewButton"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)


def _clone_repo(url: str, dest: Path, output_placeholder):
    dest.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(
        ["git", "clone", url, str(dest)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    lines = []
    for line in proc.stdout:
        lines.append(line)
        output_placeholder.code("".join(lines), language=None)
    proc.wait()
    return proc.returncode


def setup():
    st.title("Setup — Repository Configuration")
    st.markdown(
        "The app needs two local repositories to function. "
        "Point to existing clones or let the app clone them for you."
    )

    presence = repos_present()

    col1, col2 = st.columns(2)
    with col1:
        if presence["main"]:
            st.success(f"**digital-archiving-scripts** found  \n`{get_repo_root()}`")
        else:
            st.error(f"**digital-archiving-scripts** not found  \n`{get_repo_root()}`")
    with col2:
        if presence["semaphore"]:
            st.success(f"**semaphore-classification-python** found  \n`{get_semaphore_dir()}`")
        else:
            st.warning(f"**semaphore-classification-python** not found  \n`{get_semaphore_dir()}`  \n*(optional — only needed for Semaphore Classification)*")

    if all(presence.values()):
        st.info("Both repositories are present. Reload the page to continue.")
        return

    st.divider()
    tab_browse, tab_clone = st.tabs(["Point to existing repos", "Clone from GitHub"])

    with tab_browse:
        st.markdown("Enter the local paths to repositories you have already cloned.")
        new_main = st.text_input(
            "digital-archiving-scripts path",
            value=str(get_repo_root()),
            disabled=presence["main"],
        )
        new_sem = st.text_input(
            "semaphore-classification-python path",
            value=str(get_semaphore_dir()),
            disabled=presence["semaphore"],
        )
        if st.button("Save paths", type="primary"):
            updates = {}
            if not presence["main"]:
                updates["repo_root"] = new_main
            if not presence["semaphore"]:
                updates["semaphore_dir"] = new_sem
            save_paths_config(updates)
            st.rerun()

    with tab_clone:
        st.markdown("Choose a parent directory and the app will `git clone` the missing repositories into it.")
        parent = st.text_input(
            "Parent directory",
            value=str(Path.home() / "Documents" / "custom scripts"),
        )

        missing = []
        if not presence["main"]:
            missing.append(("digital-archiving-scripts", REPO_URLS["digital-archiving-scripts"]))
        if not presence["semaphore"]:
            missing.append(("semaphore-classification-python", REPO_URLS["semaphore-classification-python"]))

        for name, url in missing:
            st.markdown(f"- `{name}` — `{url}`")

        if st.button("Clone repositories", type="primary"):
            parent_path = Path(parent)
            all_ok = True
            output = st.empty()

            for name, url in missing:
                dest = parent_path / name
                st.markdown(f"Cloning `{name}`...")
                rc = _clone_repo(url, dest, output)
                if rc == 0:
                    if name == "digital-archiving-scripts":
                        save_paths_config({"repo_root": str(dest)})
                    else:
                        save_paths_config({"semaphore_dir": str(dest)})
                    st.success(f"`{name}` cloned to `{dest}`")
                else:
                    st.error(f"Failed to clone `{name}`. Check the output above.")
                    all_ok = False

            if all_ok:
                st.rerun()


def home():
    st.title("Digital Archiving Tools")
    st.caption("ICAEW digital archiving scripts — Streamlit interface")
    st.markdown("""
Use the sidebar to navigate between tools.

| Tool | Description |
|------|-------------|
| **Credentials** | Configure Preservica connection settings |
| **Get Metadata** | Export metadata and checksums from Preservica to CSV |
| **Delete Metadata** | Remove DC and ICAEW metadata from assets or folders |
| **Add Metadata** | Add DC/ICAEW metadata to assets from a CSV |
| **Update XIP** | Update titles, descriptions and security tags from a CSV |
| **Download Assets** | Download asset files from Preservica with fixity checking |
| **Move Assets** | Move assets or folders to a destination folder |
| **Build Folder Tree** | Visualise the folder hierarchy from a Preservica export CSV |
| **Thumbnails** | Add, remove or download thumbnails |
| **CSV Merge** | Merge multiple CSV files on the assetId column |
| **Score Metadata** | Score metadata quality against the ICAEW specification |
| **Video Ingest** | Upload video and subtitle files to Preservica |
| **Semaphore Classification** | Classify files using the Semaphore Classification Service |

---
Scripts that connect to Preservica require credentials to be configured first.
""")


presence = repos_present()

if not presence["main"]:
    setup()
else:
    pg = st.navigation([
        st.Page(home, title="Home"),
        st.Page("pages/1_Credentials.py",    title="Credentials"),
        st.Page("pages/2_Get_Metadata.py",   title="Get Metadata"),
        st.Page("pages/3_Delete_Metadata.py",title="Delete Metadata"),
        st.Page("pages/4_Add_Metadata.py",   title="Add Metadata"),
        st.Page("pages/5_Update_XIP.py",     title="Update XIP"),
        st.Page("pages/6_Download_Assets.py",title="Download Assets"),
        st.Page("pages/7_Move_Assets.py",    title="Move Assets"),
        st.Page("pages/8_Build_Folder_Tree.py", title="Build Folder Tree"),
        st.Page("pages/9_Thumbnails.py",     title="Thumbnails"),
        st.Page("pages/10_CSV_Merge.py",     title="CSV Merge"),
        st.Page("pages/11_Score_Metadata.py",title="Score Metadata"),
        st.Page("pages/12_Video_Ingest.py",  title="Video Ingest"),
        st.Page("pages/13_Semaphore_Classification.py", title="Semaphore Classification"),
    ])
    pg.run()
