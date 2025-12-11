import datetime as dt
from pathlib import Path

import pytest
import time_machine
from packaging import version

from pre_commit_python_eol.check_eol import (
    EOLPythonError,
    PythonRelease,
    ReleasePhase,
    RequiresPythonNotFoundError,
    _get_cached_release_cycle,
    _parse_eol_date,
    check_python_support,
)

EOL_DATE_PARSE_CASES = (
    ("2025-01-01", dt.date(year=2025, month=1, day=1)),
    ("2025-01", dt.date(year=2025, month=1, day=1)),
)


@pytest.mark.parametrize(("date_str", "truth_date"), EOL_DATE_PARSE_CASES)
def test_parse_eol_date(date_str: str, truth_date: dt.date) -> None:
    assert _parse_eol_date(date_str) == truth_date


def test_parse_eol_date_unknown_fmt_raises() -> None:
    with pytest.raises(ValueError, match="Unknown date format"):
        _ = _parse_eol_date("123456")


def test_python_release_from_json() -> None:
    sample_metadata = {
        "branch": "3.14",
        "pep": 745,
        "status": "prerelease",
        "first_release": "2025-10-07",
        "end_of_life": "2030-10",
        "release_manager": "Hugo van Kemenade",
    }

    truth_rel = PythonRelease(
        python_ver=version.Version("3.14"),
        status=ReleasePhase.PRERELEASE,
        end_of_life=dt.date(year=2030, month=10, day=1),
    )

    assert PythonRelease.from_json("3.14", metadata=sample_metadata) == truth_rel


#  Intentionally out of expected order so sorting can be checked
SAMPLE_JSON = """\
{
  "3.14": {
    "branch": "3.14",
    "pep": 745,
    "status": "prerelease",
    "first_release": "2025-10-07",
    "end_of_life": "2030-10",
    "release_manager": "Hugo van Kemenade"
  },
  "3.15": {
    "branch": "main",
    "pep": 790,
    "status": "feature",
    "first_release": "2026-10-01",
    "end_of_life": "2031-10",
    "release_manager": "Hugo van Kemenade"
  }
}
"""

TRUTH_RELEASE_CYCLE = [
    PythonRelease(
        python_ver=version.Version("3.15"),
        status=ReleasePhase.FEATURE,
        end_of_life=dt.date(year=2031, month=10, day=1),
    ),
    PythonRelease(
        python_ver=version.Version("3.14"),
        status=ReleasePhase.PRERELEASE,
        end_of_life=dt.date(year=2030, month=10, day=1),
    ),
]


def test_get_cached_release_cycle(tmp_path: Path) -> None:
    json_file = tmp_path / "cache.json"
    json_file.write_text(SAMPLE_JSON)

    release_cycle = _get_cached_release_cycle(cache_json=json_file)
    assert release_cycle == TRUTH_RELEASE_CYCLE


RELEASE_CACHE_WITH_EOL = """\
{
  "3.14": {
    "branch": "3.14",
    "pep": 745,
    "status": "prerelease",
    "first_release": "2025-10-07",
    "end_of_life": "2030-10",
    "release_manager": "Hugo van Kemenade"
  },
  "3.8": {
    "branch": "3.8",
    "pep": 569,
    "status": "end-of-life",
    "first_release": "2019-10-14",
    "end_of_life": "2024-10-07",
    "release_manager": "Lukasz Langa"
  },
  "3.7": {
    "branch": "3.7",
    "pep": 537,
    "status": "end-of-life",
    "first_release": "2018-06-27",
    "end_of_life": "2023-06-27",
    "release_manager": "Ned Deily"
  }
}
"""


@pytest.fixture
def path_with_cache(tmp_path: Path) -> tuple[Path, Path]:
    json_file = tmp_path / "cache.json"
    json_file.write_text(RELEASE_CACHE_WITH_EOL)

    return tmp_path, json_file


SAMPLE_PYPROJECT_NO_VERSION = """\
[project]
"""


def test_check_python_no_version_spec_raises(path_with_cache: tuple[Path, Path]) -> None:
    base_path, cache_path = path_with_cache
    pyproject = base_path / "pyproject.toml"
    pyproject.write_text(SAMPLE_PYPROJECT_NO_VERSION)

    with pytest.raises(RequiresPythonNotFoundError):
        check_python_support(pyproject, cache_json=cache_path)


SAMPLE_PYPROJECT_NO_EOL = """\
[project]
requires-python = ">=3.11"
"""


def test_check_python_support_no_eol(path_with_cache: tuple[Path, Path]) -> None:
    base_path, cache_path = path_with_cache
    pyproject = base_path / "pyproject.toml"
    pyproject.write_text(SAMPLE_PYPROJECT_NO_EOL)

    with time_machine.travel(dt.date(year=2025, month=5, day=1)):
        check_python_support(pyproject, cache_json=cache_path)


SAMPLE_PYPROJECT_SINGLE_EOL = """\
[project]
requires-python = ">=3.8"
"""


def test_check_python_support_single_eol_raises(path_with_cache: tuple[Path, Path]) -> None:
    base_path, cache_path = path_with_cache
    pyproject = base_path / "pyproject.toml"
    pyproject.write_text(SAMPLE_PYPROJECT_SINGLE_EOL)

    with time_machine.travel(dt.date(year=2025, month=5, day=1)):
        with pytest.raises(EOLPythonError) as e:
            check_python_support(pyproject, cache_json=cache_path)

    assert str(e.value).endswith("3.8")


SAMPLE_PYPROJECT_SINGLE_EOL_BY_DATE = """\
[project]
requires-python = ">=3.11"
"""


def test_check_python_support_single_eol_raises_by_date(path_with_cache: tuple[Path, Path]) -> None:
    base_path, cache_path = path_with_cache
    pyproject = base_path / "pyproject.toml"
    pyproject.write_text(SAMPLE_PYPROJECT_SINGLE_EOL_BY_DATE)

    with time_machine.travel(dt.date(year=2031, month=11, day=1)):
        with pytest.raises(EOLPythonError) as e:
            check_python_support(pyproject, cache_json=cache_path)

    assert str(e.value).endswith("3.14")


SAMPLE_PYPROJECT_MULTI_EOL = """\
[project]
requires-python = ">=3.7"
"""


def test_check_python_support_multi_eol_raises(path_with_cache: tuple[Path, Path]) -> None:
    base_path, cache_path = path_with_cache
    pyproject = base_path / "pyproject.toml"
    pyproject.write_text(SAMPLE_PYPROJECT_MULTI_EOL)

    with time_machine.travel(dt.date(year=2025, month=5, day=1)):
        with pytest.raises(EOLPythonError) as e:
            check_python_support(pyproject, cache_json=cache_path)

    assert str(e.value).endswith("3.7, 3.8")


def test_check_cached_python_support_no_eol(path_with_cache: tuple[Path, Path]) -> None:
    base_path, cache_path = path_with_cache
    pyproject = base_path / "pyproject.toml"
    pyproject.write_text(SAMPLE_PYPROJECT_NO_EOL)

    check_python_support(
        pyproject,
        cache_json=cache_path,
        cached=True,
    )


def test_check_cached_python_support_single_eol_raises(path_with_cache: tuple[Path, Path]) -> None:
    base_path, cache_path = path_with_cache
    pyproject = base_path / "pyproject.toml"
    pyproject.write_text(SAMPLE_PYPROJECT_SINGLE_EOL)

    with pytest.raises(EOLPythonError) as e:
        check_python_support(
            pyproject,
            cache_json=cache_path,
            cached=True,
        )

    assert str(e.value).endswith("3.8")


def test_check_cached_python_support_single_eol_no_raises_by_date(
    path_with_cache: tuple[Path, Path],
) -> None:
    base_path, cache_path = path_with_cache
    pyproject = base_path / "pyproject.toml"
    pyproject.write_text(SAMPLE_PYPROJECT_SINGLE_EOL_BY_DATE)

    with time_machine.travel(dt.date(year=2031, month=11, day=1)):
        check_python_support(
            pyproject,
            cache_json=cache_path,
            cached=True,
        )
