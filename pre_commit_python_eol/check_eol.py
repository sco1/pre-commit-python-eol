import argparse
import sys
from collections import abc
from pathlib import Path


def main(argv: abc.Sequence[str] | None = None) -> int:  # noqa: D103
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", type=Path)
    args = parser.parse_args(argv)

    ec = 0
    raise NotImplementedError
    return ec


if __name__ == "__main__":
    sys.exit(main())
