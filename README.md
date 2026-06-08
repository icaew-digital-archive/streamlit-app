# Digital Archiving Tools

A Streamlit interface for the ICAEW digital archiving scripts.

## Prerequisites

- Python 3.10+
- Git

## Setup

**1. Clone this repository**

```bash
git clone https://github.com/icaew-digital-archive/streamlit-app
cd streamlit-app
```

**2. Create and activate a virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Run the app**

```bash
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

## First-time configuration

On first launch the app will walk you through locating the two required script repositories:

- **digital-archiving-scripts** — the main Preservica scripts
- **semaphore-classification-python** — needed only for the Semaphore Classification tool

You can point the app at existing local clones or have it clone them for you.

Once the repositories are found, go to **Credentials and Configuration** in the sidebar to enter your Preservica credentials and verify the folder paths.
