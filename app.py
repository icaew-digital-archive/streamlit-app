import streamlit as st

st.set_page_config(
    page_title="Digital Archiving Tools",
    page_icon="🗄",
    layout="wide",
)

# Remove the View more / View less collapse behaviour from the sidebar nav
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
