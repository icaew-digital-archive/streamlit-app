import tempfile
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import credentials_sidebar, run_script, save_uploaded_file

credentials_sidebar()
st.title("Score Metadata")
st.caption("Score metadata quality 0–100 against the ICAEW specification (`score_metadata.py`)")

csv_file = st.file_uploader("Preservica export CSV", type=["csv"])
exclude_prefix = st.text_input(
    "Exclude path prefix (optional)",
    placeholder="e.g. Admin/",
    help="Skip assets whose preservica_path starts with this string",
)

if st.button("Run", type="primary"):
    if not csv_file:
        st.error("Upload a CSV file.")
        st.stop()

    csv_path = save_uploaded_file(csv_file, ".csv")

    out_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    out_file.close()
    out_path = out_file.name

    args = [csv_path, "--output", out_path]
    if exclude_prefix.strip():
        args += ["--exclude", exclude_prefix.strip()]

    returncode, _ = run_script("score_metadata", args)

    if returncode == 0:
        try:
            df = pd.read_csv(out_path)
            st.success(f"Scored {len(df)} assets.")

            # Summary stats
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Mean score", f"{df['total_score'].mean():.1f}")
            col2.metric("Median score", f"{df['total_score'].median():.1f}")
            col3.metric("Min score", int(df['total_score'].min()))
            col4.metric("Max score", int(df['total_score'].max()))

            # Distribution
            bands = {"0–24": 0, "25–49": 0, "50–74": 0, "75–89": 0, "90–100": 0}
            for score in df['total_score']:
                if score <= 24:
                    bands["0–24"] += 1
                elif score <= 49:
                    bands["25–49"] += 1
                elif score <= 74:
                    bands["50–74"] += 1
                elif score <= 89:
                    bands["75–89"] += 1
                else:
                    bands["90–100"] += 1

            st.subheader("Score distribution")
            dist_df = pd.DataFrame(
                {"Band": list(bands.keys()), "Count": list(bands.values())}
            )
            st.bar_chart(dist_df.set_index("Band"))

            st.subheader("Results")
            st.dataframe(df, width='stretch')

            st.download_button(
                "Download scores CSV",
                data=Path(out_path).read_bytes(),
                file_name=f"{Path(csv_file.name).stem}-scores.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.error(f"Could not read output: {e}")
    else:
        st.error("Script exited with errors. See output above.")
