import typer
from agent.core import run_agent
from agent.sandbox import is_docker_running

app = typer.Typer()


# -----------------------------
# Preflight safety check
# -----------------------------
def ensure_sandbox_ready():
    if not is_docker_running():
        raise RuntimeError(
            "❌ Docker sandbox is not running. "
            "Start Docker before running the agent."
        )


@app.command()
def run(task: str, debug: bool = False):
    """
    Run the coding agent.
    """

    try:
        # Ensure sandbox is active before anything else
        ensure_sandbox_ready()

        if debug:
            print("🧠 Running in DEBUG mode")

        result = run_agent(task)

        print("\n========================")
        print("FINAL OUTPUT")
        print("========================\n")
        print(result)

    except Exception as e:
        print("\n❌ Agent failed:\n")
        print(str(e))
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()