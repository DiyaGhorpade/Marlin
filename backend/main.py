from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import subprocess
import os

app = FastAPI()

# Allow requests from your React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or your React URL, e.g. ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Run Streamlit if not already running ---
@app.on_event("startup")
def start_streamlit():
    # Run streamlit in background
    subprocess.Popen(
        ["streamlit", "run", "dashboard.py", "--server.port", "8501"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )

@app.get("/")
def root():
    return {"status": "FastAPI backend is running 🐋"}

# --- Redirect endpoint to Streamlit ---
@app.get("/dashboards/biodiversity")
def open_biodiversity_dashboard():
    """Redirects user to the running Streamlit dashboard"""
    return RedirectResponse(url="http://localhost:8501")
