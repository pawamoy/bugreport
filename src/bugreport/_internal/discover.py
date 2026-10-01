# SPDX-License-Identifier: ISC
#
# ISC License
#
# Copyright (c) 2025, Timothée Mazzucotelli and contributors
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

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
    """Clone a Git repository and return the contents of its first bug-template YAML file.

    Parameters:
        origin: Git repository URL or local path.
        path: Directory to check out and search for a `.yml` file with `bug` in its name.

    Raises:
        FileNotFoundError: No matching file was found.
        subprocess.CalledProcessError: A Git command failed.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        _git(["clone", "--no-checkout", "--depth=1", "--filter=tree:0", origin, "."], cwd=tmpdir)
        _git(["sparse-checkout", "set", path], cwd=tmpdir)
        _git(["checkout"], cwd=tmpdir)
        for file in Path(tmpdir).rglob("*.yml"):
            if file.is_file() and "bug" in file.stem.lower():
                return file.read_text()
    raise FileNotFoundError(f"No bugreport file found in {origin} at path {path}.")
