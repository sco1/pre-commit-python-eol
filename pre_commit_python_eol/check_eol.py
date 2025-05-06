import argparse
import sys
from collections import abc
from pathlib import Path


class EOLPythonError(Exception): ...  # noqa: D101


def _get_supported_python(toml_file: Path) -> None:
    raise NotImplementedError


def _get_cached_release_cycle() -> None:
    raise NotImplementedError


def _get_release_cycle() -> None:
    raise NotImplementedError


def check_python_support(toml_file: Path) -> None:
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

    return ec


if __name__ == "__main__":
    sys.exit(main())
