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

"""BugReport package.

Maintainers store configuration in their repository, users call the tool to generate high quality bug reports easily.
"""

from __future__ import annotations

from bugreport._internal.cli import get_parser, main
from bugreport._internal.discover import discover
from bugreport._internal.forms import FormApp
from bugreport._internal.metadata import evaluate_section_condition, render_output_template, yield_bugreport_forms
from bugreport._internal.models.bugreport import (
    BugreportElement,
    BugreportForm,
    BugreportInput,
    BugreportInputBoolean,
    BugreportInputChoice,
    BugreportInputChoices,
    BugreportInputPath,
    BugreportInputString,
    BugreportInputText,
    BugreportMarkdown,
    BugreportStep,
    TypeBugreportInput,
)
from bugreport._internal.models.github import (
    GitHubCheckboxOption,
    GitHubElementCheckboxes,
    GitHubElementDropdown,
    GitHubElementInput,
    GitHubElementMarkdown,
    GitHubElementTextarea,
    GitHubForm,
    TypeGitHubElement,
)

__all__: list[str] = [
    "BugreportElement",
    "BugreportForm",
    "BugreportInput",
    "BugreportInputBoolean",
    "BugreportInputChoice",
    "BugreportInputChoices",
    "BugreportInputPath",
    "BugreportInputString",
    "BugreportInputText",
    "BugreportMarkdown",
    "BugreportStep",
    "FormApp",
    "GitHubCheckboxOption",
    "GitHubElementCheckboxes",
    "GitHubElementDropdown",
    "GitHubElementInput",
    "GitHubElementMarkdown",
    "GitHubElementTextarea",
    "GitHubForm",
    "TypeBugreportInput",
    "TypeGitHubElement",
    "discover",
    "evaluate_section_condition",
    "get_parser",
    "main",
    "render_output_template",
    "yield_bugreport_forms",
]
