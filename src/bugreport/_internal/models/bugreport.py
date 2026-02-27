"""Bugreport metadata models used by issue-template enhancements."""

from __future__ import annotations
from docutils.nodes import subtitle

from pydantic import BaseModel, Field

from bugreport._internal.models.github import (
    GitHubElementDropdown,
    GitHubElementInput,
    GitHubElementMarkdown,
    GitHubElementTextarea,
    GitHubElementCheckboxes,
    GitHubForm,
)


class BugreportElement(BaseModel):
    """Base class for bugreport elements."""

    id: str


class BugreportMarkdown(BugreportElement):
    """Markdown element."""

    value: str


class BugreportInput(BugreportElement):
    """Input base model."""

    required: bool = False
    label: str | None = None
    description: str | None = None
    placeholder: str | None = None


class BugreportInputString(BugreportInput):
    """String input."""

    highlight: str | None = None
    value: str | None = None


class BugreportInputChoice(BugreportInput):
    """Choice input."""

    options: dict[str, str] | None = None
    value: str | None = None


class BugreportInputChoices(BugreportInput):
    """Choices input."""

    options: dict[str, str] | None = None
    value: str | None = None


class BugreportInputText(BugreportInput):
    """Text input."""

    highlight: str | None = None
    value: str | None = None


class BugreportInputBoolean(BugreportInput):
    """Boolean input."""

    value: bool | None = None


class BugreportInputPath(BugreportInput):
    """Path input."""

    value: str | None = None


TypeBugreportInput = (
    BugreportInputString
    | BugreportInputChoice
    | BugreportInputChoices
    | BugreportInputText
    | BugreportInputBoolean
    | BugreportInputPath
)


class BugreportStep(BaseModel):
    """Step model."""

    slug: str | None = None
    title: str | None = None
    description: str | None = None
    condition: str | None = Field(default=None, alias="if")
    body: list[TypeBugreportInput | BugreportMarkdown] = Field(default_factory=list)
    outputs: dict[str, str] = Field(default_factory=dict)


class BugreportForm(BaseModel):
    """Bugreport metadata root model."""

    title: str | None = None
    subtitle: str | None = None
    body: list[BugreportStep | BugreportMarkdown] = Field(default_factory=list)

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
                body.append(BugreportStep(inputs=[input_element]))
            elif isinstance(element, GitHubElementDropdown):
                input_element = BugreportInputChoice(
                    id=element.id or "",
                    label=element.label,
                    description=element.description,
                    options={option: option for option in element.options},
                    required=element.required,
                )
                body.append(BugreportStep(inputs=[input_element]))
            elif isinstance(element, GitHubElementCheckboxes):
                input_element = BugreportInputChoices(
                    id=element.id or "",
                    label=element.label,
                    description=element.description,
                    options={option.id or option.label: option.label for option in element.options},
                    required=element.required,
                )
                body.append(BugreportStep(inputs=[input_element]))
        return cls(body=body)
