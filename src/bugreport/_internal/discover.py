import subprocess
import tempfile
from pathlib import Path


def _git(args: list[str], cwd: str | None = None) -> str:
    process = subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return process.stdout


def discover(origin: str, path: str = ".github/ISSUE_TEMPLATE") -> str:
    """Discover the path to the bugreport file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _git(["clone", "--no-checkout", "--depth=1", "--filter=tree:0", origin, "."], cwd=tmpdir)
        _git(["sparse-checkout", "set", path], cwd=tmpdir)
        _git(["checkout"], cwd=tmpdir)
        for file in Path(tmpdir).rglob("*.yml"):
            if file.is_file() and "bug" in file.stem.lower():
                return file.read_text()
    raise FileNotFoundError(f"No bugreport file found in {origin} at path {path}.")
