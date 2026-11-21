"""One-command check: every test under tests/, then the text lint (tools/batches.py). The pre-commit hook runs this."""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = [sys.executable, "-X", "utf8"]
steps = [PY + ["-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"],
         PY + ["tools/batches.py", "--selftest"],
         PY + ["tools/batches.py", "check"]]
sys.exit(max(subprocess.call(s, cwd=ROOT) for s in steps))
