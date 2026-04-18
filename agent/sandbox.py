import subprocess
import tempfile
import os
import uuid
import time
import sys


DOCKER_IMAGE = "python:3.11-slim"

CPU_LIMIT = "0.5"
MEM_LIMIT = "256m"
TIMEOUT_SECONDS = 5


# -----------------------------
# Docker health check
# -----------------------------
def is_docker_running():
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False


# -----------------------------
# Attempt to start Docker (best-effort)
# -----------------------------
def try_start_docker():
    """
    Attempts to start Docker depending on OS.
    This is best-effort only.
    """

    platform = sys.platform

    try:
        # Linux (systemd)
        if platform.startswith("linux"):
            subprocess.run(
                ["systemctl", "start", "docker"],
                capture_output=True,
                text=True
            )
            time.sleep(2)
            return is_docker_running()

        # macOS (Docker Desktop)
        elif platform == "darwin":
            # This may or may not work depending on install
            subprocess.Popen(
                ["open", "-a", "Docker"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(5)
            return is_docker_running()

        # Windows (best effort)
        elif platform.startswith("win"):
            subprocess.run(
                ["powershell", "Start-Service", "docker"],
                capture_output=True,
                text=True
            )
            time.sleep(3)
            return is_docker_running()

    except Exception:
        pass

    return False


# -----------------------------
# Ensure Docker is available
# -----------------------------
def ensure_docker():
    if is_docker_running():
        return True

    print("[SANDBOX] Docker not running. Attempting to start...")

    if try_start_docker():
        print("[SANDBOX] Docker started successfully.")
        return True

    raise RuntimeError(
        "Docker is not running and could not be started automatically. "
        "Please start Docker manually."
    )


# -----------------------------
# Main sandbox execution
# -----------------------------
def run_code_safely(code: str):
    ensure_docker()

    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            f.write(code.encode("utf-8"))
            temp_file_path = f.name

        container_name = f"agent_sandbox_{uuid.uuid4().hex}"

        cmd = [
            "docker", "run", "--rm",
            "--name", container_name,

            "--cpus", CPU_LIMIT,
            "--memory", MEM_LIMIT,
            "--network", "none",
            "--security-opt", "no-new-privileges",

            "-v", f"{temp_file_path}:/app/code.py:ro",
            "-w", "/app",

            DOCKER_IMAGE,
            "python", "code.py"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS
        )

        return {
            "returncode": result.returncode,
            "stdout": result.stdout[-10000:],
            "stderr": result.stderr[-10000:]
        }

    except subprocess.TimeoutExpired:
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": "Execution timed out (container killed)"
        }

    except Exception as e:
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": f"Sandbox error: {str(e)}"
        }

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass