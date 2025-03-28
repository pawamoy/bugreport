from typing import Literal, Union

from pydantic import BaseModel

ElementType = Literal["checkboxes", "dropdown", "input", "markdown", "textarea"]


class MarkdownAttributes(BaseModel):
    value: str


class TextareaAttributes(BaseModel):
    label: str
    description: str | None = ""
    placeholder: str | None = ""
    value: str | None = ""
    render: str | None = None


class InputAttributes(BaseModel):
    label: str
    description: str | None = ""
    placeholder: str | None = ""
    value: str | None = ""


class DropdownAttributes(BaseModel):
    label: str
    description: str | None = ""
    multiple: bool | None = False
    options: list[str]
    default: int | None = None


class CheckboxOption(BaseModel):
    label: str
    required: bool | None = False


class CheckboxesAttributes(BaseModel):
    label: str
    description: str | None = ""
    options: list[CheckboxOption]


class Validations(BaseModel):
    required: bool | None = False


Attributes = Union[MarkdownAttributes,  TextareaAttributes,  InputAttributes,  DropdownAttributes,  CheckboxesAttributes]
AttributesWithLabelDescription = Union[TextareaAttributes,  InputAttributes,  DropdownAttributes,  CheckboxesAttributes]

class FormElement(BaseModel):
    type: ElementType
    id: str | None = None
    attributes: Attributes
    validations: Validations | None = None


class Form(BaseModel):
    body: list[FormElement]
