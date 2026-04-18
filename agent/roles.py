from .llm import call_llm


# -----------------------------
# Planner (structured steps)
# -----------------------------
def planner(task):
    return call_llm(
        system=(
            "You are a senior software engineer.\n"
            "Break tasks into clear implementation steps.\n"
            "Return ONLY a numbered list of steps.\n"
            "No explanations."
        ),
        user=task,
        temperature=0.4
    )


# -----------------------------
# Coder (strict implementation)
# -----------------------------
def coder(step, context=""):
    return call_llm(
        system=(
            "You are a production-grade software engineer.\n"
            "Write correct, minimal, dependency-safe code.\n"
            "Do NOT include explanations.\n"
            "Return ONLY code."
        ),
        user=f"Step:\n{step}\n\nContext:\n{context}",
        temperature=0.1
    )


# -----------------------------
# Reviewer (structured decision)
# -----------------------------
def reviewer(code):
    return call_llm(
        system=(
            "You are a strict code reviewer.\n"
            "Evaluate correctness, security, and clarity.\n"
            "Return ONLY one line in this format:\n"
            "APPROVED\n"
            "or\n"
            "REJECTED: <reason>"
        ),
        user=code,
        temperature=0.0
    )


# -----------------------------
# Test generator (strict pytest output)
# -----------------------------
def tester(code):
    return call_llm(
        system=(
            "You write pytest tests.\n"
            "Return ONLY valid pytest code.\n"
            "No explanations, no markdown."
        ),
        user=code,
        temperature=0.2
    )


# -----------------------------
# Fixer (patch-style behavior)
# -----------------------------
def fixer(code, feedback):
    return call_llm(
        system=(
            "You are a debugging assistant.\n"
            "Fix ONLY what is necessary.\n"
            "Do not rewrite unrelated parts.\n"
            "Return ONLY corrected full code."
        ),
        user=f"Code:\n{code}\n\nFeedback:\n{feedback}",
        temperature=0.1
    )