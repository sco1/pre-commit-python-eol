# pre-commit-python-eol
[![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fsco1%2Fpre-commit-python-eol%2Frefs%2Fheads%2Fmain%2Fpyproject.toml&logo=python&logoColor=FFD43B)](https://github.com/sco1/pre-commit-python-eol/blob/main/pyproject.toml)
[![GitHub Release](https://img.shields.io/github/v/release/sco1/pre-commit-python-eol)](https://github.com/sco1/pre-commit-python-eol/releases)
[![GitHub License](https://img.shields.io/github/license/sco1/pre-commit-python-eol?color=magenta)](https://github.com/sco1/pre-commit-python-eol/blob/main/LICENSE)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sco1/pre-commit-python-eol/main.svg)](https://results.pre-commit.ci/latest/github/sco1/pre-commit-python-eol/main)

A pre-commit hook for enforcing supported [Python EOL](https://devguide.python.org/versions/).

## Using `pre-commit-python-eol` With pre-commit
Add this to your `.pre-commit-config.yaml`

```yaml
-   repo: https://github.com/sco1/pre-commit-python-eol
    rev: v2026.1.0
    hooks:
    - id: check-eol
    - id: check-eol-cached
```

While both hooks are technically compatible with each other, it's advised to choose a single hook behavior that best fits your needs.

### EOL Status Cache
To avoid requiring network connectivity at runtime, EOL status is cached to [a local JSON file](./pre_commit_python_eol/cached_release_cycle.json) distributed alongside this hook. The cache is updated quarterly & a changed cache will result in a version bump for this hook.

## Hooks
Only `pyproject.toml` is currently inspected. It is assumed that project metadata is specified per [PyPA Guidance](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)

### `check-eol`
Check `requires-python` against the current Python lifecycle & fail if an EOL version is included; this includes a date-based check using the system's time for versions that have not yet explicitly been declared EOL.

### `check-eol-cached`
Check `requires-python` against the current Python lifecycle & fail if an EOL version is included; this hook utilizes only the cached release cycle information.

## Python Version Support
Starting with Python 3.11, a best attempt is made to support Python versions until they reach EOL, after which support will be formally dropped by the next minor or major release of this package, whichever arrives first. The status of Python versions can be found [here](https://devguide.python.org/versions/).
