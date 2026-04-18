from pathlib import Path
import yaml
from .roles import planner, coder, reviewer, fixer, tester
from .tester import generate_tests, write_test_file, run_tests, write_code_to_workspace
from .safety import validate_code

# -----------------------------
# Load config safely
# -----------------------------
CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.yaml"
with open(CONFIG_PATH, "r") as f:
    CONFIG = yaml.safe_load(f)

# -----------------------------
# State container
# -----------------------------
def init_state(task: str):
    return {
        "task": task,
        "plan": [],
        "completed_steps": [],
        "context": "",
        "final_code": "",
    }

# -----------------------------
# Helpers
# -----------------------------
def safe_call(fn, *args, fallback=None):
    try:
        return fn(*args)
    except Exception as e:
        print(f"[ERROR] {fn.__name__} failed:", e)
        return fallback

def update_context(context: str, new_code: str, max_chars: int = 12000):
    """
    Prevent unbounded context growth. Keeps most recent content only.
    """
    updated = context + "\n\n" + new_code
    if len(updated) > max_chars:
        return updated[-max_chars:]
    return updated

# -----------------------------
# Main agent loop
# -----------------------------
def run_agent(task: str):
    state = init_state(task)
    print("🧠 Planning...")
    plan = safe_call(planner, task, fallback="")
    if not plan:
        print("[ERROR] Planner returned empty plan.")
        return ""

    # Normalize plan into steps
    state["plan"] = [
        line.strip("-• \t") for line in plan.split("\n") if line.strip()
    ]
    final_code = ""

    # -------------------------
    # Step execution loop
    # -------------------------
    for i, step in enumerate(state["plan"]):
        print(f"\n➡️ Step {i+1}: {step}")

        # Generate code
        code = safe_call(coder, step, state["context"], fallback="")
        if not code:
            print("[WARN] Skipping step due to empty code.")
            continue

        # Safety check
        safe, msg = validate_code(code)
        if not safe:
            print(f"[BLOCKED] Safety violation: {msg}")
            continue

        # Review step
        review = safe_call(reviewer, code, fallback="APPROVED")
        
        # Simple but safer interpretation
        if isinstance(review, str) and "reject" in review.lower():
            print("[REVIEW] Code rejected → fixing...")
            code = safe_call(fixer, code, review, fallback=code)

        # Generate tests
        tests = safe_call(tester, code, fallback="")
        if tests:
            write_test_file(tests)
        
        # **CRITICAL FIX**: Write the generated code to workspace so tester can run it
        write_code_to_workspace(code)

        # -------------------------
        # Test loop
        # -------------------------
        max_iters = CONFIG.get("testing", {}).get("max_iterations", 3)
        for _ in range(max_iters):
            passed, output = run_tests()
            if passed:
                print("✅ Tests passed")
                break
            print("🔧 Fixing failing tests...")
            code = safe_call(fixer, code, output, fallback=code)
            # **CRITICAL FIX**: Update the code file after fixing
            write_code_to_workspace(code)

        # Update state
        state["context"] = update_context(state["context"], code)
        state["completed_steps"].append(step)
        final_code = code

    state["final_code"] = final_code
    return final_code
