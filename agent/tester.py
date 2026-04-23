import subprocess
import os
import tempfile
import uuid

DOCKER_ = "python:3.11-slim"

def write_test_file(test_code, path="workspace/test_generated.py"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(test_code)

def write_code_to_workspace(code, path="workspace/main.py"):
    """
    Writes the generated code to the workspace directory so tests can import/run it.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(code)

# -----------------------------
# Run pytest inside Docker
# -----------------------------
def run_tests():
    container_name = f"pytest_runner_{uuid.uuid4().hex}"
    workspace_path = os.path.abspath("workspace")
    
    try:
        os.makedirs(workspace_path, exist_ok=True)
        cmd = [
            "docker", "run", "--rm", "--name", container_name,
            # Mount workspace as read-write (rw) so pytest can create .pytest_cache
            "-v", f"{workspace_path}:/app/workspace:rw",
            "-w", "/app/workspace",
            DOCKER_,
            "bash", "-lc",
            "pip install pytest >/dev/null 2>&1 && PYTHONPATH=. pytest . --maxfail=1 --disable-warnings -q"
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=15
        )
        success = result.returncode == 0
        output = (result.stdout or "") + (result.stderr or "")
        return success, output[-10000:]
    except subprocess.TimeoutExpired:
        return False, "pytest timed out"
    except Exception as e:
        return False, f"test runner error: {str(e)}"
