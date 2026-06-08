import os
import sys
import subprocess
import tempfile
from pathlib import Path

import streamlit as st

REPO_ROOT = Path(__file__).parent.parent / "digital-archiving-scripts"
PYPRESERVICA_DIR = REPO_ROOT / "pypreservica scripts"
CSV_TOOLS_DIR = REPO_ROOT / "csv-tools"
VIDEO_INGEST_DIR = PYPRESERVICA_DIR / "pypreservica-video-package-ingest"
SEMAPHORE_DIR = Path("/home/digital-archivist/Documents/custom scripts/semaphore-classification-python")
ENV_FILE = REPO_ROOT / ".env"


SCRIPTS = {
    "get_metadata":    PYPRESERVICA_DIR / "a_get_metadata.py",
    "delete_metadata": PYPRESERVICA_DIR / "b_delete_metadata.py",
    "add_metadata":    PYPRESERVICA_DIR / "c_add_metadata_from_csv.py",
    "update_xip":      PYPRESERVICA_DIR / "d_update_xip_from_csv.py",
    "download":        PYPRESERVICA_DIR / "download_preservica_assets.py",
    "move":            PYPRESERVICA_DIR / "move_preservica_assets.py",
    "build_tree":      PYPRESERVICA_DIR / "build_preservica_tree.py",
    "thumbnails":      PYPRESERVICA_DIR / "remove_thumbnails.py",
    "csv_merge":       CSV_TOOLS_DIR / "csv_merge.py",
    "score_metadata":  CSV_TOOLS_DIR / "score_metadata.py",
    "video_ingest":    VIDEO_INGEST_DIR / "video_subtitle_package_ingest.py",
    "semaphore":       SEMAPHORE_DIR / "semaphore_helper.py",
}

SCRIPT_CWD = {
    "semaphore": SEMAPHORE_DIR,
}


def load_env_file():
    """Read key=value pairs from the repo .env file. Returns dict of keys to values."""
    result = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                key, _, value = line.partition("=")
                result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def write_env_file(values: dict):
    """Write credential keys to the repo .env file, preserving other keys."""
    existing = {}
    lines = []
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            stripped = line.strip()
            if stripped and "=" in stripped and not stripped.startswith("#"):
                key, _, _ = stripped.partition("=")
                existing[key.strip()] = len(lines)
            lines.append(line)

    for key, value in values.items():
        if key in existing:
            lines[existing[key]] = f"{key}={value}"
        else:
            lines.append(f"{key}={value}")

    ENV_FILE.write_text("\n".join(lines) + "\n")


def credentials_valid():
    env = load_env_file()
    return all(env.get(k) for k in ("USERNAME", "PASSWORD", "TENANT", "SERVER"))


def credentials_sidebar():
    with st.sidebar:
        if credentials_valid():
            st.success("Credentials loaded")
        else:
            st.warning("Credentials missing — see Credentials page")


def save_uploaded_file(uploaded_file, suffix=None):
    """Save an uploaded Streamlit file to a temp file. Returns the path string."""
    if suffix is None:
        suffix = Path(uploaded_file.name).suffix or ".tmp"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(uploaded_file.getvalue())
    tmp.close()
    return tmp.name


def save_text_as_file(text, suffix=".txt"):
    """Save a string to a temp file and return the path."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode="w", encoding="utf-8")
    tmp.write(text)
    tmp.close()
    return tmp.name


def save_refs_as_csv(refs_text):
    """Save newline-separated references as a CSV with an assetId header row."""
    import csv as _csv
    refs = [r.strip() for r in refs_text.splitlines() if r.strip()]
    tmp = tempfile.NamedTemporaryFile(
        delete=False, suffix=".csv", mode="w", encoding="utf-8", newline=""
    )
    writer = _csv.writer(tmp)
    writer.writerow(["assetId"])
    for ref in refs:
        writer.writerow([ref])
    tmp.close()
    return tmp.name


def run_script(script_key, args, stdin_input=None):
    """
    Run one of the named scripts as a subprocess from the repo root.
    Streams stdout to a Streamlit code block. Returns (returncode, full_output).

    If stdin_input is a string, it is fed to the process stdin (used for
    scripts that prompt for confirmation).
    """
    script_path = SCRIPTS[script_key]
    cmd = [sys.executable, str(script_path)] + [str(a) for a in args]

    env = os.environ.copy()
    env.update(load_env_file())
    env["PYTHONUNBUFFERED"] = "1"
    env["DOWNLOAD_SCRIPT"] = str(SCRIPTS["download"])

    cwd = str(SCRIPT_CWD.get(script_key, REPO_ROOT))

    if stdin_input is not None:
        # Use communicate() to avoid pipe deadlock when stdin is needed
        with st.spinner("Running..."):
            try:
                result = subprocess.run(
                    cmd,
                    input=stdin_input,
                    capture_output=True,
                    text=True,
                    env=env,
                    cwd=cwd,
                )
                output = result.stdout + (result.stderr or "")
                st.code(output, language=None)
                return result.returncode, output
            except Exception as e:
                st.error(str(e))
                return 1, str(e)
    else:
        output_container = st.empty()
        output_lines = []
        MAX_DISPLAY_LINES = 200
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                cwd=cwd,
                bufsize=1,
            )
            for line in proc.stdout:
                output_lines.append(line)
                display = output_lines[-MAX_DISPLAY_LINES:]
                output_container.code("".join(display), language=None)
            proc.wait()
            return proc.returncode, "".join(output_lines)
        except Exception as e:
            st.error(str(e))
            return 1, str(e)
