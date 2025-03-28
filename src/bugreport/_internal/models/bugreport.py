from __future__ import annotations

from pathlib import Path
from typing import Final, Literal, Union

from pydantic import BaseModel, Field

InputType = Literal["string", "text", "choice", "choices", "boolean", "path"]


class Input(BaseModel):
    """Input base model."""

    id: str
    required: bool = False
    label: str | None = None
    description: str | None = None
    placeholder: str | None = None


class StringInput(Input):
    """String input."""

    type: Final = "string"
    highlight: str | None = None
    value: str | None = None


class ChoiceInput(Input):
    """Choice input."""

    type: Final = "choice"
    options: dict[str, str] | None = None
    value: str | None = None


class ChoicesInput(Input):
    """Choices input."""

    type: Final = "choices"
    options: dict[str, str] | None = None
    value: str | None = None


class TextInput(Input):
    """Text input."""

    type: Final = "text"
    highlight: str | None = None
    value: str | None = None


class BooleanInput(Input):
    """Boolean input."""

    type: Final = "boolean"
    value: bool | None = None


class PathInput(Input):
    """Path input."""

    type: Final = "path"
    value: Path | None = None


FormInput = Union[StringInput, ChoiceInput, ChoicesInput, TextInput, BooleanInput, PathInput]


class FormSection(BaseModel):
    """Section model."""

    title: str | None = None
    description: str | None = None
    condition: str | None = Field(default=None, alias="if")
    inputs: list[FormInput] = Field(default_factory=list)
    outputs: dict[str, str] = Field(default_factory=dict)


class Form(BaseModel):
    sections: list[FormSection]
