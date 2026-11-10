"""Bare `cvforge` (no subcommand) must exit 2 like other usage errors, not 0."""

import subprocess
import sys

CODE = "import sys; from cvforge.cli import main; main()"


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-c", CODE, *args],
        capture_output=True,
        text=True,
    )


def test_bare_invocation_exits_2():
    proc = run_cli()
    assert proc.returncode == 2
    assert "usage" in proc.stdout.lower()


def test_unknown_command_exits_2():
    proc = run_cli("frobnicate")
    assert proc.returncode == 2
