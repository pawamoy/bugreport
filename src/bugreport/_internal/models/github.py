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

from __future__ import annotations

import logging

from pydantic import BaseModel

_logger = logging.getLogger("bugreport")


class GitHubElementMarkdown(BaseModel):
    """Markdown instructions in a GitHub issue form."""

    id: str | None = None
    """Optional identifier for the element."""
    value: str
    """Markdown content to display."""


class GitHubElementTextarea(BaseModel):
    """An input for several lines of text in a GitHub issue form."""

    id: str | None = None
    """Optional identifier for the input."""
    label: str
    """Label displayed above the input."""
    description: str | None = ""
    """Markdown instructions displayed below the label."""
    placeholder: str | None = ""
    """Hint displayed when the input is empty."""
    value: str | None = ""
    """Initial text content."""
    render: str | None = None
    """Language used to render the submitted text as a code block."""
    required: bool = False
    """Whether the user must provide a value."""


class GitHubElementInput(BaseModel):
    """An input for a single line of text in a GitHub issue form."""

    id: str | None = None
    """Optional identifier for the input."""
    label: str
    """Label displayed above the input."""
    description: str | None = ""
    """Markdown instructions displayed below the label."""
    placeholder: str | None = ""
    """Hint displayed when the input is empty."""
    value: str | None = ""
    """Initial input value."""
    required: bool = False
    """Whether the user must provide a value."""


class GitHubElementDropdown(BaseModel):
    """A list of options to select in a GitHub issue form."""

    id: str | None = None
    """Optional identifier for the dropdown."""
    label: str
    """Label displayed above the dropdown."""
    description: str | None = ""
    """Markdown instructions displayed below the label."""
    multiple: bool | None = False
    """Whether the form allows several options to be selected."""
    options: list[str]
    """Option labels in display order."""
    default: int | None = None
    """Index of the initially selected option."""
    required: bool = False
    """Whether the user must select an option."""


class GitHubCheckboxOption(BaseModel):
    """One checkbox option in a GitHub issue form."""

    id: str | None = None
    """Optional identifier for the option."""
    label: str
    """Label displayed beside the checkbox."""
    required: bool | None = False
    """Whether the user must select the checkbox."""


class GitHubElementCheckboxes(BaseModel):
    """A group of checkbox options in a GitHub issue form."""

    id: str | None = None
    """Optional identifier for the group."""
    label: str
    """Label displayed above the checkboxes."""
    description: str | None = ""
    """Markdown instructions displayed below the label."""
    options: list[GitHubCheckboxOption]
    """Checkbox options in display order."""
    required: bool = False
    """Whether the group requires a selection."""


TypeGitHubElement = (
    GitHubElementMarkdown | GitHubElementTextarea | GitHubElementInput | GitHubElementDropdown | GitHubElementCheckboxes
)
"""Supported GitHub issue-form element types."""


class GitHubForm(BaseModel):
    """The supported elements of a GitHub issue form."""

    body: list[TypeGitHubElement]
    """Form elements in display order."""

    @classmethod
    def from_data(cls, data: dict) -> GitHubForm:
        """Parse an issue-template mapping, logging and skipping unsupported element types."""
        body = []
        for element_data in data.get("body", []):
            element_type = element_data.get("type")
            required = element_data.get("validations", {}).get("required", False)
            if element_type == "markdown":
                element = GitHubElementMarkdown(**element_data["attributes"])
            elif element_type == "textarea":
                element = GitHubElementTextarea(**element_data["attributes"], required=required)
            elif element_type == "input":
                element = GitHubElementInput(**element_data["attributes"], required=required)
            elif element_type == "dropdown":
                element = GitHubElementDropdown(**element_data["attributes"], required=required)
            elif element_type == "checkbox":
                options = [GitHubCheckboxOption(**option) for option in element_data["attributes"]["options"]]
                element_data["attributes"]["options"] = options
                element = GitHubElementCheckboxes(**element_data["attributes"], required=required)
            else:
                _logger.error(f"Unsupported element type: {element_type}")
                continue
            body.append(element)
        return cls(body=body)
