from __future__ import annotations

import logging
from typing import Self, Union

from pydantic import BaseModel

_logger = logging.getLogger("bugreport")


class GitHubElementMarkdown(BaseModel):
    id: str | None = None
    value: str
    required: bool = False


class GitHubElementTextarea(BaseModel):
    id: str | None = None
    label: str
    description: str | None = ""
    placeholder: str | None = ""
    value: str | None = ""
    render: str | None = None
    required: bool = False


class GitHubElementInput(BaseModel):
    id: str | None = None
    label: str
    description: str | None = ""
    placeholder: str | None = ""
    value: str | None = ""
    required: bool = False


class GitHubElementDropdown(BaseModel):
    id: str | None = None
    label: str
    description: str | None = ""
    multiple: bool | None = False
    options: list[str]
    default: int | None = None
    required: bool = False


class GitHubCheckboxOption(BaseModel):
    id: str | None = None
    label: str
    required: bool | None = False


class GitHubElementCheckboxes(BaseModel):
    id: str | None = None
    label: str
    description: str | None = ""
    options: list[GitHubCheckboxOption]
    required: bool = False


TypeGitHubElement = Union[
    GitHubElementMarkdown,
    GitHubElementTextarea,
    GitHubElementInput,
    GitHubElementDropdown,
    GitHubElementCheckboxes,
]


class GitHubForm(BaseModel):
    body: list[TypeGitHubElement]

    @classmethod
    def from_data(cls, data: dict) -> Self:
        """Create a Form instance from raw data."""
        body = []
        for element_data in data.get("body", []):
            element_type = element_data.get("type")
            required = element_data.get("validations", {}).get("required", False)
            if element_type == "markdown":
                element = GitHubElementMarkdown(**element_data["attributes"], required=required)
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
