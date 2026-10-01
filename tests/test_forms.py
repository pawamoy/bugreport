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

import asyncio
from typing import TYPE_CHECKING

import yaml
from textual.widgets import Input, Markdown, TextArea

from bugreport._internal.forms import FormApp
from bugreport._internal.models.bugreport import (
    BugreportForm,
    BugreportInputChoice,
    BugreportInputChoices,
    BugreportInputString,
    BugreportStep,
)
from bugreport._internal.models.github import (
    GitHubCheckboxOption,
    GitHubElementCheckboxes,
    GitHubElementDropdown,
    GitHubElementInput,
    GitHubForm,
)

if TYPE_CHECKING:
    from pathlib import Path


def test_conversion_preserves_inputs() -> None:
    # Each supported GitHub input must survive conversion to a step body.
    github_form = GitHubForm(
        body=[
            GitHubElementInput(id="name", label="Name"),
            GitHubElementDropdown(id="version", label="Version", options=["stable"]),
            GitHubElementCheckboxes(id="confirmed", label="Confirmed", options=[GitHubCheckboxOption(label="Yes")]),
        ],
    )

    form = BugreportForm.from_github(github_form)

    assert len(form.body) == 3
    for step, input_type, input_id in zip(
        form.body,
        (BugreportInputString, BugreportInputChoice, BugreportInputChoices),
        ("name", "version", "confirmed"),
        strict=True,
    ):
        assert isinstance(step, BugreportStep)
        assert len(step.body) == 1
        assert isinstance(step.body[0], input_type)
        assert step.body[0].id == input_id


def test_form_renders_metadata_and_updates_outputs(tmp_path: Path) -> None:
    # Include markdown and a step so both form body variants are rendered.
    metadata = {
        "bugreport": {
            "body": [
                {"id": "intro", "value": "Metadata instructions"},
                {
                    "title": "Details",
                    "body": [{"id": "name", "label": "Name", "value": "initial"}],
                    "outputs": {"summary": "Name: {{ inputs.name }}"},
                },
            ],
        },
    }
    template = {
        "body": [
            {"type": "markdown", "attributes": {"value": f"<!--\n{yaml.safe_dump(metadata)}-->"}},
            {"type": "textarea", "attributes": {"label": "Summary", "value": "Original summary"}},
        ],
    }
    template_path = tmp_path / "issue.yml"
    template_path.write_text(yaml.safe_dump(template), encoding="utf-8")
    app = FormApp(issue_template=str(template_path))

    async def exercise_form() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()

            assert any(markdown.source == "Metadata instructions" for markdown in app.query(Markdown))
            assert app.query_one(TextArea).text == "Original summary"

            # Editing a metadata input must render its step's output.
            app.query_one("#name", Input).value = "updated"
            await pilot.pause()

            assert app.form_outputs == {"summary": "Name: updated"}

    asyncio.run(exercise_form())
