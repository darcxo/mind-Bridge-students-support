#!/usr/bin/env python3
"""
MindBridge — One-click start script
Run: python run.py
Then open: http://localhost:8000
"""
import subprocess, sys, os, pathlib

ROOT = pathlib.Path(__file__).parent
BACKEND = ROOT / "backend"

def install_deps():
    print("📦 Installing dependencies...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-r",
        str(BACKEND / "requirements.txt"), "-q"
    ])
    print("✅ Dependencies ready!\n")

def start_server():
    print("=" * 50)
    print("  🧠 MindBridge — Mental Health Support App")
    print("=" * 50)
    print("🌐 Open your browser at: http://localhost:8000")
    print("📖 API docs at:          http://localhost:8000/docs")
    print("Press Ctrl+C to stop.\n")

    os.chdir(str(BACKEND))
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "main:app", "--host", "0.0.0.0",
        "--port", "8000", "--reload"
    ])

if __name__ == "__main__":
    install_deps()
    start_server()
