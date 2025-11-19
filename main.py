import sys
from pathlib import Path

# Add project root to path so src module can be imported
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn


def run_api():
    """Run FastAPI server."""
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


def run_chainlit():
    """Run Chainlit interface."""
    import subprocess

    subprocess.run(["chainlit", "run", "src/ui/chainlit_app.py", "--port", "8001"])


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "chainlit":
        print("Starting Chainlit interface on http://localhost:8001")
        run_chainlit()
    else:
        print("Starting FastAPI server on http://localhost:8000")
        print("API Docs: http://localhost:8000/docs")
        run_api()
