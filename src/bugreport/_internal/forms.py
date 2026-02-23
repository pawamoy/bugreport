from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Checkbox, Input, Label, Markdown, Select, TextArea

from bugreport._internal.metadata import (
    evaluate_section_condition,
    load_bugreport_metadata_from_github_form,
    render_output_template,
)
from bugreport._internal.models.bugreport import (
    BugreportFormSection,
    BugreportInputBoolean,
    BugreportInputChoice,
    BugreportInputChoices,
    BugreportInputPath,
    BugreportInputString,
    BugreportInputText,
    TypeBugreportInput,
)
from bugreport._internal.models.github import (
    GitHubElementCheckboxes,
    GitHubElementDropdown,
    GitHubElementInput,
    GitHubElementMarkdown,
    GitHubElementTextarea,
    GitHubForm,
    TypeGitHubElement,
)


class FormApp(App[None]):
    CSS_PATH = Path(__file__).parent / "forms.tcss"

    def __init__(self, issue_template: str = ".github/ISSUE_TEMPLATE/1-bug.yml", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.issue_template = issue_template
        self.github_form: GitHubForm | None = None
        self.form_inputs: dict[str, Any] = {}
        self.form_outputs: dict[str, str] = {}
        self._section_containers: list[tuple[BugreportFormSection, Vertical]] = []
        self._metadata_outputs: dict[str, str] = {}
        self._metadata_textareas: dict[str, TextArea] = {}

    def compose(self) -> ComposeResult:
        with Path(self.issue_template).open(encoding="utf-8") as file:
            form_data = yaml.safe_load(file)
        self.github_form = GitHubForm.from_data(form_data)

        for element in self.github_form.body:
            yield from self._create_widgets(element)
            if isinstance(element, GitHubElementMarkdown):
                for block in load_bugreport_metadata_from_github_form(element):
                    for section in block.form.sections:
                        container = Vertical(classes="metadata-section")
                        self._section_containers.append((section, container))
                        with container:
                            if section.title:
                                yield Label(section.title)
                            if section.description:
                                yield Markdown(section.description)
                            for metadata_input in section.inputs:
                                yield from self._create_metadata_input_widgets(metadata_input)
                        yield container
                        self._metadata_outputs.update(section.outputs)

        self._update_metadata_sections_and_outputs()

    def _create_label(self, label: str | None) -> ComposeResult:
        if label:
            yield Label(label)

    def _create_description(self, description: str | None) -> ComposeResult:
        if description:
            yield Markdown(description)

    def _create_textarea(self, attributes: GitHubElementTextarea, element_id: str | None = None) -> ComposeResult:
        yield from self._create_label(attributes.label)
        yield from self._create_description(attributes.description)
        textarea_id = f"github__{element_id}" if element_id else None
        if attributes.render:
            textarea = TextArea.code_editor(attributes.value or "", language=attributes.render, id=textarea_id)
        else:
            textarea = TextArea(attributes.value or "", id=textarea_id)
        if element_id:
            self._metadata_textareas[element_id] = textarea
        yield textarea

    def _create_input(self, attributes: GitHubElementInput, element_id: str | None = None) -> ComposeResult:
        yield from self._create_label(attributes.label)
        yield from self._create_description(attributes.description)
        yield Input(
            attributes.value,
            placeholder=attributes.placeholder or "",
            id=f"github__{element_id}" if element_id else None,
        )

    def _create_dropdown(self, attributes: GitHubElementDropdown, element_id: str | None = None) -> ComposeResult:
        yield from self._create_label(attributes.label)
        yield from self._create_description(attributes.description)
        value = attributes.options[attributes.default] if attributes.default is not None else Select.BLANK
        select = Select(
            [(option, option) for option in attributes.options],
            value=value,
            allow_blank=attributes.default is None,
            type_to_search=False,
            id=f"github__{element_id}" if element_id else None,
        )
        yield select

    def _create_checkboxes(self, attributes: GitHubElementCheckboxes, element_id: str | None = None) -> ComposeResult:
        yield from self._create_label(attributes.label)
        yield from self._create_description(attributes.description)
        for index, option in enumerate(attributes.options):
            suffix = f"{element_id}_{index}" if element_id else str(index)
            yield Checkbox(
                option.label,
                value=bool(option.required),
                disabled=bool(option.required),
                id=f"github__{suffix}",
            )

    def _create_markdown(self, attributes: GitHubElementMarkdown) -> ComposeResult:
        yield Markdown(attributes.value)

    def _create_widgets(self, element: TypeGitHubElement) -> ComposeResult:
        if isinstance(element, GitHubElementTextarea):
            yield from self._create_textarea(element, element.id)
        elif isinstance(element, GitHubElementInput):
            yield from self._create_input(element, element.id)
        elif isinstance(element, GitHubElementDropdown):
            yield from self._create_dropdown(element, element.id)
        elif isinstance(element, GitHubElementCheckboxes):
            yield from self._create_checkboxes(element, element.id)
        elif isinstance(element, GitHubElementMarkdown):
            yield from self._create_markdown(element)

    def _create_metadata_input_widgets(
        self,
        metadata_input: TypeBugreportInput,
    ) -> ComposeResult:
        yield from self._create_label(metadata_input.label)
        yield from self._create_description(metadata_input.description)

        if isinstance(metadata_input, (BugreportInputString, BugreportInputPath)):
            value = str(metadata_input.value) if metadata_input.value is not None else ""
            self.form_inputs.setdefault(metadata_input.id, value)
            yield Input(value=value, placeholder=metadata_input.placeholder or "", id=metadata_input.id)
            return

        if isinstance(metadata_input, BugreportInputText):
            value = metadata_input.value or ""
            self.form_inputs.setdefault(metadata_input.id, value)
            if metadata_input.highlight:
                yield TextArea.code_editor(value, language=metadata_input.highlight, id=metadata_input.id)
            else:
                yield TextArea(value, id=metadata_input.id)
            return

        if isinstance(metadata_input, BugreportInputChoice):
            options = list((metadata_input.options or {}).items())
            if not options:
                return
            value = metadata_input.value if metadata_input.value is not None else options[0][0]
            self.form_inputs.setdefault(metadata_input.id, value)
            yield Select(
                [(label, key) for key, label in options],
                value=value,
                allow_blank=False,
                type_to_search=False,
                id=metadata_input.id,
            )
            return

        if isinstance(metadata_input, BugreportInputChoices):
            selected = set(metadata_input.value.split(",")) if metadata_input.value else set()
            self.form_inputs.setdefault(metadata_input.id, sorted(selected))
            for option_key, option_label in (metadata_input.options or {}).items():
                checkbox_id = f"{metadata_input.id}__{option_key}"
                yield Checkbox(option_label, value=option_key in selected, id=checkbox_id)
            return

        if isinstance(metadata_input, BugreportInputBoolean):
            value = bool(metadata_input.value)
            self.form_inputs.setdefault(metadata_input.id, value)
            label = metadata_input.placeholder or metadata_input.label or metadata_input.id
            yield Checkbox(label, value=value, id=metadata_input.id)

    def _update_metadata_sections_and_outputs(self) -> None:
        active_outputs: dict[str, str] = {}
        for section, container in self._section_containers:
            visible = evaluate_section_condition(section.condition, self.form_inputs)
            container.display = visible
            if visible:
                active_outputs.update(section.outputs)

        rendered_outputs: dict[str, str] = {}
        for output_name, template in active_outputs.items():
            rendered_outputs[output_name] = render_output_template(template, self.form_inputs, rendered_outputs)

        self.form_outputs = rendered_outputs
        for output_name, value in rendered_outputs.items():
            if output_name in self._metadata_textareas:
                self._metadata_textareas[output_name].load_text(value)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id:
            self.form_inputs[event.input.id] = event.value
            self._update_metadata_sections_and_outputs()

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        if event.text_area.id:
            self.form_inputs[event.text_area.id] = event.text_area.text
            self._update_metadata_sections_and_outputs()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id:
            self.form_inputs[event.select.id] = event.value
            self._update_metadata_sections_and_outputs()

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        checkbox_id = event.checkbox.id
        if not checkbox_id:
            return

        if "__" in checkbox_id:
            input_id, option_key = checkbox_id.split("__", 1)
            values = set(self.form_inputs.get(input_id, []))
            if event.value:
                values.add(option_key)
            else:
                values.discard(option_key)
            self.form_inputs[input_id] = sorted(values)
        else:
            self.form_inputs[checkbox_id] = event.value

        self._update_metadata_sections_and_outputs()


if __name__ == "__main__":
    FormApp().run()
