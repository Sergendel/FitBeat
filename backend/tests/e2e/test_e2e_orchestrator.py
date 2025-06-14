# tests/e2e/test_e2e_orchestrator.py

import subprocess
import sys
from pathlib import Path


def test_orchestrator_e2e():
    # Run orchestrator as module to verify full import path correctness
    result = subprocess.run(
        [sys.executable, "-m", "backend.core.orchestrator"],
        capture_output=True,
        text=True,
        cwd=Path(__file__)
        .resolve()
        .parent.parent.parent,  # ensures running from project root
    )
    # Print stdout and stderr after subprocess finishes
    print("=== Subprocess STDOUT ===")
    print(result.stdout)
    print("=== Subprocess STDERR ===")
    print(result.stderr)

    assert result.returncode == 0, f"Orchestrator failed: {result.stderr}"
