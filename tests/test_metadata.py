from __future__ import annotations

from pathlib import Path

import yaml

from bugreport._internal.metadata import (
    evaluate_section_condition,
    iter_bugreport_metadata_blocks,
    load_bugreport_metadata_from_github_form,
    render_output_template,
)
from bugreport._internal.models.github import Form as GithubForm


def test_extract_metadata_block_from_markdown_comment() -> None:
    markdown = """\
Before.
<!--
bugreport:
  sections:
    - inputs:
        - id: sample
          type: string
-->
After.
"""
    blocks = iter_bugreport_metadata_blocks(markdown)
    assert len(blocks) == 1
    assert blocks[0].form.sections[0].inputs[0].id == "sample"


def test_load_metadata_from_issue_template() -> None:
    template = Path(".github/ISSUE_TEMPLATE/1-bug.yml")
    with template.open(encoding="utf-8") as file:
        github_form = GithubForm(**yaml.safe_load(file))

    blocks = load_bugreport_metadata_from_github_form(github_form)

    assert len(blocks) >= 1
    assert any(section.outputs for block in blocks for section in block.form.sections)


def test_evaluate_section_condition() -> None:
    inputs = {"run_mre": True, "mre_option": "url"}
    assert evaluate_section_condition("inputs.run_mre", inputs)
    assert evaluate_section_condition('inputs.mre_option == "url"', inputs)
    assert not evaluate_section_condition('inputs.mre_option == "path"', inputs)
    assert not evaluate_section_condition("inputs.unknown", inputs)


def test_render_output_template() -> None:
    template = """\
{% if inputs.mre_url %}
{{ inputs.mre_url }}
{% endif %}
{{ outputs.previous }}
"""
    rendered = render_output_template(template, {"mre_url": "https://example.test/repro"}, {"previous": "done"})
    assert "https://example.test/repro" in rendered
    assert "done" in rendered
