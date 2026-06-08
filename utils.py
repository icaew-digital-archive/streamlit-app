import json
import os
import sys
import subprocess
import tempfile
from pathlib import Path

import streamlit as st

PATHS_CONFIG = Path(__file__).parent / "paths.json"

_DEFAULT_REPO_ROOT = Path(__file__).parent.parent / "digital-archiving-scripts"
_DEFAULT_SEMAPHORE_DIR = Path("/home/digital-archivist/Documents/custom scripts/semaphore-classification-python")

REPO_URLS = {
    "digital-archiving-scripts": "https://github.com/icaew-digital-archive/digital-archiving-scripts",
    "semaphore-classification-python": "https://github.com/icaew-digital-archive/semaphore-classification-python",
}


def load_paths_config() -> dict:
    if PATHS_CONFIG.exists():
        try:
            return json.loads(PATHS_CONFIG.read_text())
        except Exception:
            pass
    return {}


def save_paths_config(values: dict):
    existing = load_paths_config()
    existing.update(values)
    PATHS_CONFIG.write_text(json.dumps(existing, indent=2))


def get_repo_root() -> Path:
    cfg = load_paths_config()
    if cfg.get("repo_root"):
        return Path(cfg["repo_root"])
    return _DEFAULT_REPO_ROOT


def get_semaphore_dir() -> Path:
    cfg = load_paths_config()
    if cfg.get("semaphore_dir"):
        return Path(cfg["semaphore_dir"])
    return _DEFAULT_SEMAPHORE_DIR


def get_env_file() -> Path:
    return Path(__file__).parent / ".env"


def repos_present() -> dict:
    """Returns dict with 'main' and 'semaphore' bools indicating which repos exist."""
    return {
        "main": get_repo_root().exists(),
        "semaphore": get_semaphore_dir().exists(),
    }


def _get_scripts() -> dict:
    repo_root = get_repo_root()
    pypreservica = repo_root / "pypreservica scripts"
    csv_tools = repo_root / "csv-tools"
    video_ingest = pypreservica / "pypreservica-video-package-ingest"
    semaphore = get_semaphore_dir()
    return {
        "get_metadata":    pypreservica / "a_get_metadata.py",
        "delete_metadata": pypreservica / "b_delete_metadata.py",
        "add_metadata":    pypreservica / "c_add_metadata_from_csv.py",
        "update_xip":      pypreservica / "d_update_xip_from_csv.py",
        "download":        pypreservica / "download_preservica_assets.py",
        "move":            pypreservica / "move_preservica_assets.py",
        "build_tree":      pypreservica / "build_preservica_tree.py",
        "thumbnails":      pypreservica / "remove_thumbnails.py",
        "csv_merge":       csv_tools / "csv_merge.py",
        "score_metadata":  csv_tools / "score_metadata.py",
        "video_ingest":    video_ingest / "video_subtitle_package_ingest.py",
        "semaphore":       semaphore / "semaphore_helper.py",
    }


def _get_script_cwd() -> dict:
    return {"semaphore": get_semaphore_dir()}


def load_env_file():
    """Read key=value pairs from the repo .env file. Returns dict of keys to values."""
    result = {}
    env_file = get_env_file()
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                key, _, value = line.partition("=")
                result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def write_env_file(values: dict):
    """Write credential keys to the repo .env file, preserving other keys."""
    env_file = get_env_file()
    existing = {}
    lines = []
    if env_file.exists():
        for line in env_file.read_text().splitlines():
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

    env_file.write_text("\n".join(lines) + "\n")


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
    scripts = _get_scripts()
    script_path = scripts[script_key]
    cmd = [sys.executable, str(script_path)] + [str(a) for a in args]

    env = os.environ.copy()
    env.update(load_env_file())
    env["PYTHONUNBUFFERED"] = "1"
    env["DOWNLOAD_SCRIPT"] = str(scripts["download"])

    cwd = str(_get_script_cwd().get(script_key, get_repo_root()))

    if stdin_input is not None:
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
