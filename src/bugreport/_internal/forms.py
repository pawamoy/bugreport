from pathlib import Path
from typing import cast
import yaml
from textual.app import App, ComposeResult
from textual.widgets import Checkbox, Select, Input, Label, TextArea, Markdown

from bugreport._internal.models.github import (
    CheckboxesAttributes,
    DropdownAttributes,
    FormElement,
    Form,
    InputAttributes,
    MarkdownAttributes,
    TextareaAttributes, Attributes,
    AttributesWithLabelDescription,
)


class FormApp(App):
    CSS_PATH = Path(__file__).parent / "forms.tcss"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_form_data = {}
        self.current_form_index = 0

    # https://github.com/Textualize/textual/discussions/3968
    # https://textual.textualize.io/tutorial/#dynamic-widgets
    # https://textual.textualize.io/how-to/render-and-compose/

    def compose(self) -> ComposeResult:
        with open(".github/ISSUE_TEMPLATE/1-bug.yml") as file:
            form_data = yaml.safe_load(file)
        self.form = Form(**form_data)
        self.render_form(self.form.body[self.current_form_index])

    def render_form(self, element: FormElement):
        self.view.clear()
        yield from self.create_widgets(element)
        yield Button("Next", on_click=self.on_next_click)

    # def compose(self) -> ComposeResult:
    #     with open(".github/ISSUE_TEMPLATE/1-bug.yml") as file:
    #         form_data = yaml.safe_load(file)
    #     form = Form(**form_data)
    #     for element in form.body:
    #         yield from self.create_widgets(element)

    def create_label(self, attributes: AttributesWithLabelDescription):
        if attributes.label:
            yield Label(attributes.label)

    def create_description(self, attributes: AttributesWithLabelDescription):
        if attributes.description:
            yield Markdown(attributes.description)

    def create_textarea(self, attributes: TextareaAttributes):
        yield from self.create_label(attributes)
        yield from self.create_description(attributes)
        if attributes.render:
            yield TextArea.code_editor(
                attributes.value or "",
                language=attributes.render,
            )
        else:
            yield TextArea(attributes.value or "")

    def create_input(self, attributes: InputAttributes):
        yield from self.create_label(attributes)
        yield from self.create_description(attributes)
        yield Input(
            attributes.value,
            placeholder=attributes.placeholder or "",
        )

    def create_dropdown(self, attributes: DropdownAttributes):
        yield from self.create_label(attributes)
        yield from self.create_description(attributes)
        yield Select(
            [(option, option) for option in attributes.options],
            value=attributes.options[attributes.default] if attributes.default is not None else None,
            allow_blank=attributes.default is None,
            type_to_search=False,
        )

    def create_checkboxes(self, attributes: CheckboxesAttributes):
        yield from self.create_label(attributes)
        yield from self.create_description(attributes)
        for option in attributes.options:
            yield Checkbox(option.label, value=bool(option.required), disabled=bool(option.required))

    def create_markdown(self, attributes: MarkdownAttributes):
        yield Markdown(attributes.value)

    def create_widgets(self, element: FormElement):
        if element.type == "textarea":
            yield from self.create_textarea(element.attributes)  # type: ignore[arg-type]
        elif element.type == "input":
            yield from self.create_input(element.attributes)  # type: ignore[arg-type]
        elif element.type == "dropdown":
            yield from self.create_dropdown(element.attributes)  # type: ignore[arg-type]
        elif element.type == "checkboxes":
            yield from self.create_checkboxes(element.attributes)  # type: ignore[arg-type]
        elif element.type == "markdown":
            yield from self.create_markdown(element.attributes)  # type: ignore[arg-type]

    async def on_next_click(self, event):
        # Store current form data
        for widget in self.view.children:
            if isinstance(widget, Input):
                self.current_form_data[widget.id] = widget.value
            elif isinstance(widget, TextArea):
                self.current_form_data[widget.id] = widget.value
            elif isinstance(widget, Select):
                self.current_form_data[widget.id] = widget.value
            elif isinstance(widget, Checkbox):
                self.current_form_data[widget.id] = widget.value

        # Move to the next form element
        self.current_form_index += 1
        if self.current_form_index < len(self.form.body):
            self.render_form(self.form.body[self.current_form_index])
        else:
            # Handle form completion
            self.on_form_complete()

    def on_form_complete(self):
        self.view.clear()
        yield Label("Form completed!")
        yield Markdown(f"Collected data: {self.current_form_data}")

if __name__ == "__main__":
    FormApp().run()
