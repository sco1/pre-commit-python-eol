from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import tomllib
import typing as t
from collections import abc
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from packaging import specifiers, version

CACHED_RELEASE_CYCLE = Path("./cached_release_cycle.json")


class EOLPythonError(Exception): ...  # noqa: D101


class RequiresPythonNotFoundError(Exception): ...  # noqa: D101


class ReleasePhase(StrEnum):
    """
    Python release phase mapping, as described by PEP602.

    See: https://devguide.python.org/versions/#status-key
    """

    FEATURE = "feature"
    PRERELEASE = "prerelease"
    BUGFIX = "bugfix"
    SECURITY = "security"
    EOL = "end-of-life"


def _parse_eol_date(date_str: str) -> dt.date:
    """
    Parse a `dt.date` instance from one of two specification formats.

    Two date formats are supported:
        * `YYYY-MM-DD` - Parsed as-is, assuming ISO 8601 format
        * `YYYY-MM` - Parsed as a `dt.date` instance for the 1st of the specified year & month
    """
    parts = date_str.split("-")
    match len(parts):
        case 3:
            eol_date = dt.date.fromisoformat(date_str)
        case 2:
            year, month = (int(c) for c in parts)
            eol_date = dt.date(year=year, month=month, day=1)
        case _:
            raise ValueError(f"Unknown date format: '{date_str}'")

    return eol_date


@dataclass(frozen=True)
class PythonRelease:
    """
    Represent the relevant metadata information for a Python release.

    For the purposes of this tool, instances of `PythonRelease` are considered equal if their
    respective `python_ver` attributes are equal.
    """

    python_ver: version.Version
    status: ReleasePhase
    end_of_life: dt.date

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PythonRelease):
            return NotImplemented

        return self.python_ver == other.python_ver

    def __str__(self) -> str:
        return f"Python {self.python_ver} - Status: {self.status}, EOL: {self.end_of_life}"

    @classmethod
    def from_json(cls, ver: str, metadata: dict[str, t.Any]) -> PythonRelease:
        """
        Create a `PythonRelease` instance from the provided JSON components.

        JSON components are assumed to be of the format provided by the Python Devguide:
        https://github.com/python/devguide/blob/main/include/release-cycle.json
        """
        return cls(
            python_ver=version.Version(ver),
            status=ReleasePhase(metadata["status"]),
            end_of_life=_parse_eol_date(metadata["end_of_life"]),
        )


def _get_cached_release_cycle(cache_json: Path = CACHED_RELEASE_CYCLE) -> set[PythonRelease]:
    """Parse the locally cached Python release cycle into `PythonRelease` instance(s)."""
    with cache_json.open("r", encoding="utf-8") as f:
        contents = json.load(f)

    return {PythonRelease.from_json(v, m) for v, m in contents.items()}


def check_python_support(toml_file: Path) -> None:
    with toml_file.open("rb") as f:
        contents = tomllib.load(f)

    requires_python = contents.get("project", {}).get("requires-python", None)
    if not requires_python:
        raise RequiresPythonNotFoundError

    package_spec = specifiers.SpecifierSet(requires_python)

    raise NotImplementedError


def main(argv: abc.Sequence[str] | None = None) -> int:  # noqa: D103
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", type=Path)
    args = parser.parse_args(argv)

    ec = 0
    for file in args.filenames:
        try:
            check_python_support(file)
        except EOLPythonError:
            print(f"{file}: Fail.")
            ec = 1
        except RequiresPythonNotFoundError:
            print(f"{file} 'requires-python' could not be located, or it is empty.")
            ec = 1

    return ec


if __name__ == "__main__":
    sys.exit(main())
