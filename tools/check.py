"""One-command check: every test under tests/ (plus text lint once it exists). The pre-commit hook runs this."""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.exit(subprocess.call([sys.executable, "-X", "utf8", "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"], cwd=ROOT))
