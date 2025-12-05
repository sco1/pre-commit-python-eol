import json
import platform
from pathlib import Path

from pre_commit_python_eol import __url__, __version__

try:
    import httpx
except ImportError:
    raise RuntimeError(
        "httpx was not installed, please install the 'gha' dependency group"
    ) from None

USER_AGENT = (
    f"pre-commit-check-eol/{__version__} ({__url__}) "
    f"httpx/{httpx.__version__} "
    f"{platform.python_implementation()}/{platform.python_version()}"
)

CACHE_SOURCE = "https://peps.python.org/api/release-cycle.json"
LOCAL_CACHE = Path("./pre_commit_python_eol/cached_release_cycle.json")


def bump_cache() -> None:
    """Update the cached release cycle JSON from the source repository."""
    with httpx.Client(headers={"User-Agent": USER_AGENT}) as client:
        r = client.get(CACHE_SOURCE)
        r.raise_for_status()

        rj = r.json()

    with LOCAL_CACHE.open("w", encoding="utf8") as f:
        json.dump(rj, f, indent=2, ensure_ascii=False)
        f.write("\n")  # Add in trailing newline


if __name__ == "__main__":
    bump_cache()
