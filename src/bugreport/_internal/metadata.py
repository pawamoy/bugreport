from __future__ import annotations

import fnmatch
import logging
import re
from dataclasses import dataclass
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

import yaml
from jinja2 import Environment

from bugreport._internal import debug
from bugreport._internal.models.bugreport import Form as BugreportForm

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

    from bugreport._internal.models.github import GitHubElementMarkdown


_logger = logging.getLogger("bugreport")


_BUGREPORT_HTML_COMMENT_RE = re.compile(r"<!--(?P<content>.*?)-->", re.DOTALL)
_BUGREPORT_KEY = "bugreport"
_TRUE_CONDITION = re.compile(r"^inputs\.([A-Za-z_][A-Za-z0-9_]*)$")
_EQUALS_CONDITION = re.compile(r'^inputs\.([A-Za-z_][A-Za-z0-9_]*)\s*==\s*(["\'])(.*?)\2$')


@dataclass(frozen=True)
class MetadataBlock:
    """Metadata block extracted from a markdown element."""

    raw: str
    form: BugreportForm


class _TemplateVenvInfo:
    """Simple object exposed to templates for environment info."""

    def __init__(self) -> None:
        self._env = debug._get_debug_info()

    @property
    def platform(self) -> str:
        return self._env.platform

    @property
    def interpreter_name(self) -> str:
        return self._env.interpreter_name

    @property
    def interpreter_version(self) -> str:
        return self._env.interpreter_version

    @property
    def interpreter_path(self) -> str:
        return self._env.interpreter_path

    def env_vars(self, *patterns: str) -> list[tuple[str, str]]:
        names = [variable.name for variable in self._env.variables]
        selected = [name for name in names if any(fnmatch.fnmatch(name, pattern) for pattern in patterns)]
        values = {variable.name: variable.value for variable in self._env.variables}
        return [(name, values[name]) for name in selected]

    def packages(self, *patterns: str) -> list[tuple[str, str]]:
        names = [package.name for package in self._env.packages]
        selected = [name for name in names if any(fnmatch.fnmatch(name, pattern) for pattern in patterns)]
        versions = {package.name: package.version for package in self._env.packages}
        return [(name, versions[name]) for name in selected]


def _to_namespace(data: dict[str, Any]) -> SimpleNamespace:
    return SimpleNamespace(**data)


def _to_block(content: str) -> MetadataBlock | None:
    try:
        loaded = yaml.safe_load(content)
    except yaml.YAMLError as error:
        _logger.debug(f"Failed to parse YAML content in metadata block: {error}")
        return None
    if not isinstance(loaded, dict):
        return None
    root = loaded.get(_BUGREPORT_KEY)
    if not isinstance(root, dict):
        return None
    return MetadataBlock(raw=content, form=BugreportForm.model_validate(root))


def iter_bugreport_metadata_blocks(markdown: str) -> Iterator[MetadataBlock]:
    """Extract bugreport metadata blocks from markdown HTML comments."""
    for match in _BUGREPORT_HTML_COMMENT_RE.finditer(markdown):
        if block := _to_block(match.group("content")):
            yield block


def load_bugreport_metadata_from_github_form(element: GitHubElementMarkdown) -> list[MetadataBlock]:
    """Load bugreport metadata from a GitHub form element."""
    return list(iter_bugreport_metadata_blocks(element.value))


def evaluate_section_condition(condition: str | None, inputs: dict[str, Any]) -> bool:
    """Evaluate a minimal condition syntax used by metadata sections."""
    if not condition:
        return True
    if (match := _TRUE_CONDITION.fullmatch(condition.strip())) is not None:
        return bool(inputs.get(match.group(1)))
    if (match := _EQUALS_CONDITION.fullmatch(condition.strip())) is not None:
        return str(inputs.get(match.group(1), "")) == match.group(3)
    return False


def _mre_path(path: str) -> str:
    return f"```bash\n# path to MRE\n{path}\n```"


def _mre_url(commands: str) -> str:
    return f"```bash\n{commands.strip()}\n```"


def _mre_code(code: str, language: str = "python") -> str:
    return f"```{language}\n{code.rstrip()}\n```"


def _mre_commands(commands: str) -> str:
    return f"```bash\n{commands.strip()}\n```"


def _run_mre(_mre: str) -> str:
    return "Automatic MRE execution is not implemented yet in the TUI preview."


def _venv_info(_path: str | Path | None = None) -> _TemplateVenvInfo:
    return _TemplateVenvInfo()


def render_output_template(template: str, inputs: dict[str, Any], outputs: dict[str, str]) -> str:
    """Render a metadata output template with current inputs and previously rendered outputs."""
    environment = Environment(autoescape=True, trim_blocks=True, lstrip_blocks=True)
    environment.filters.update(
        {
            "mre_path": _mre_path,
            "mre_url": _mre_url,
            "mre_code": _mre_code,
            "mre_commands": _mre_commands,
            "run_mre": _run_mre,
            "venv_info": _venv_info,
        },
    )
    rendered = environment.from_string(template).render(
        inputs=_to_namespace(inputs),
        outputs=_to_namespace(outputs),
    )
    return rendered.strip()
