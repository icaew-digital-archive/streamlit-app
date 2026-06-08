import tempfile
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import credentials_sidebar, run_script, save_uploaded_file

credentials_sidebar()
st.title("Build Folder Tree")
st.caption("Visualise the Preservica folder hierarchy from a CSV export (`build_preservica_tree.py`)")
st.info("Expects a Preservica full-export CSV containing `preservica_path`, `assetId` and `entity.entity_type` columns.")

csv_file = st.file_uploader("Input CSV", type=["csv"])

col1, col2 = st.columns(2)
with col1:
    depth = st.number_input("Max depth (0 = unlimited)", min_value=0, value=0, step=1)
    show_ids = st.checkbox("Show folder IDs")
with col2:
    include_assets = st.checkbox("Include assets (default: folders only)")

if st.button("Run", type="primary"):
    if not csv_file:
        st.error("Upload a CSV file.")
        st.stop()

    csv_path = save_uploaded_file(csv_file, ".csv")
    out_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    out_file.close()
    out_path = out_file.name

    args = [csv_path, "--output", out_path]
    if depth > 0:
        args += ["--depth", str(int(depth))]
    if show_ids:
        args.append("--show-ids")
    if include_assets:
        args.append("--include-assets")

    returncode, _ = run_script("build_tree", args)

    if returncode == 0:
        tree_text = Path(out_path).read_text(encoding="utf-8")
        st.success("Done.")
        st.code(tree_text, language=None)
        st.download_button(
            "Download tree (.txt)",
            data=tree_text,
            file_name=f"{Path(csv_file.name).stem}-folders-tree.txt",
            mime="text/plain",
        )
    else:
        st.error("Script exited with errors. See output above.")
