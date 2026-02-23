"""Bugreport metadata models used by issue-template enhancements."""

from __future__ import annotations

from pydantic import BaseModel, Field


class BugreportInput(BaseModel):
    """Input base model."""

    id: str
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


class BugreportFormSection(BaseModel):
    """Section model."""

    title: str | None = None
    description: str | None = None
    condition: str | None = Field(default=None, alias="if")
    inputs: list[TypeBugreportInput] = Field(default_factory=list)
    outputs: dict[str, str] = Field(default_factory=dict)


class BugreportForm(BaseModel):
    """Bugreport metadata root model."""

    sections: list[BugreportFormSection] = Field(default_factory=list)
