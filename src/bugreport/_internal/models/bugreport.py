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

from pydantic import BaseModel, Field

from bugreport._internal.models.github import (
    GitHubElementCheckboxes,
    GitHubElementDropdown,
    GitHubElementInput,
    GitHubElementMarkdown,
    GitHubForm,
)


class BugreportElement(BaseModel):
    """Base class for bugreport elements."""

    id: str
    """Identifier used to reference the element in templates and widgets."""


class BugreportMarkdown(BugreportElement):
    """Markdown instructions displayed in a bugreport form."""

    value: str
    """Markdown content to display."""


class BugreportInput(BugreportElement):
    """Common settings for a bugreport input."""

    required: bool = False
    """Whether the user must provide a value."""
    label: str | None = None
    """Label displayed above the input."""
    description: str | None = None
    """Markdown instructions displayed below the label."""
    placeholder: str | None = None
    """Hint displayed when the input is empty."""


class BugreportInputString(BugreportInput):
    """A single line of text in a bugreport form."""

    highlight: str | None = None
    """Requested syntax highlighting language."""
    value: str | None = None
    """Initial input value."""


class BugreportInputChoice(BugreportInput):
    """An input for selecting one option."""

    options: dict[str, str] | None = None
    """Option values mapped to their displayed labels."""
    value: str | None = None
    """Initially selected option value."""


class BugreportInputChoices(BugreportInput):
    """An input for selecting several options."""

    options: dict[str, str] | None = None
    """Option values mapped to their displayed labels."""
    value: str | None = None
    """Initially selected option values, separated by commas."""


class BugreportInputText(BugreportInput):
    """Several lines of text in a bugreport form."""

    highlight: str | None = None
    """Syntax highlighting language for the text editor."""
    value: str | None = None
    """Initial text content."""


class BugreportInputBoolean(BugreportInput):
    """A checkbox in a bugreport form."""

    value: bool | None = None
    """Initial checkbox state."""


class BugreportInputPath(BugreportInput):
    """An input for a filesystem path."""

    value: str | None = None
    """Initial path value."""


TypeBugreportInput = (
    BugreportInputString
    | BugreportInputChoice
    | BugreportInputChoices
    | BugreportInputText
    | BugreportInputBoolean
    | BugreportInputPath
)
"""Supported bugreport input types."""


class BugreportStep(BaseModel):
    """A group of inputs with an optional condition and output templates."""

    slug: str | None = None
    """Identifier for the step."""
    title: str | None = None
    """Title displayed above the step."""
    description: str | None = None
    """Markdown instructions for the step."""
    condition: str | None = Field(default=None, alias="if")
    """Condition that controls whether the step is displayed."""
    body: list[TypeBugreportInput | BugreportMarkdown] = Field(default_factory=list)
    """Inputs and Markdown instructions in display order."""
    outputs: dict[str, str] = Field(default_factory=dict)
    """Output names mapped to Jinja templates for their values."""


class BugreportForm(BaseModel):
    """A bugreport form defined in issue-template metadata."""

    title: str | None = None
    """Title of the form."""
    subtitle: str | None = None
    """Additional text below the title."""
    body: list[BugreportStep | BugreportMarkdown] = Field(default_factory=list)
    """Steps and Markdown instructions in display order."""

    @classmethod
    def from_github(cls, form: GitHubForm) -> BugreportForm:
        """Convert a GitHub form to a Bugreport form."""
        body: list[BugreportStep | BugreportMarkdown] = []
        for element in form.body:
            if isinstance(element, GitHubElementMarkdown):
                body.append(BugreportMarkdown(id=element.id or "", value=element.value))
            elif isinstance(element, GitHubElementInput):
                input_element = BugreportInputString(
                    id=element.id or "",
                    label=element.label,
                    description=element.description,
                    placeholder=element.placeholder,
                    required=element.required,
                )
                body.append(BugreportStep(body=[input_element]))
            elif isinstance(element, GitHubElementDropdown):
                input_element = BugreportInputChoice(
                    id=element.id or "",
                    label=element.label,
                    description=element.description,
                    options={option: option for option in element.options},
                    required=element.required,
                )
                body.append(BugreportStep(body=[input_element]))
            elif isinstance(element, GitHubElementCheckboxes):
                input_element = BugreportInputChoices(
                    id=element.id or "",
                    label=element.label,
                    description=element.description,
                    options={option.id or option.label: option.label for option in element.options},
                    required=element.required,
                )
                body.append(BugreportStep(body=[input_element]))
        return cls(body=body)
