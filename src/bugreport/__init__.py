"""BugReport package.

Maintainers store configuration in their repository, users call the tool to generate high quality bug reports easily.
"""

from __future__ import annotations

from bugreport._internal.cli import get_parser, main

__all__: list[str] = ["get_parser", "main"]
