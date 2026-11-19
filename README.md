# molars_lcmtypes

[LCM](https://lcm-proj.github.io/lcm/) message, service and action types for [MOLARS](https://github.com/CoMPASLab/molars).

The MOLARS types build on the shared CoMPAS types (`stdlcm`, `senlcm`, `navlcm`, `geolcm`) from [compas_lcmtypes](https://github.com/CoMPASLab/compas_lcmtypes), which this package depends on.

## Layout

The `.lcm` sources are organized by LCM package:

```
control_server/   action/<name>/  msg/  srv/<name>/
health/           srv/<name>/
lcm_action_server/msg/  srv/<name>/
mission_server/   action/<name>/  srv/<name>/
nav_server/       action/<name>/  msg/  srv/<name>/
```

Services have `_request`/`_response` types and actions have `_goal`/`_result`/`_feedback` types. To scaffold a new interface, run from the repository root:

```bash
python generate.py <package> {msg,srv,action} <name>
```

## Python package

The `molars-lcmtypes` Python package is generated with `lcm-gen` at build time and installs under the `molars_lcmtypes` namespace, mirroring `compas_lcmtypes`:

```python
from molars_lcmtypes.nav_server.msg import waypoint
from compas_lcmtypes.stdlcm import header_t
```

References to CoMPAS types inside MOLARS types resolve to `compas_lcmtypes`. Fingerprints, and therefore the wire format, are the same as types generated without a package prefix.

Releases are published as GitHub releases (not PyPI). Install a release with:

```bash
uv add "molars-lcmtypes @ git+https://github.com/CoMPASLab/molars_lcmtypes@vX.Y.Z"
# or
pip install "molars-lcmtypes @ git+https://github.com/CoMPASLab/molars_lcmtypes@vX.Y.Z"
```

Building from source requires network access for the `lcm` build dependency, which provides `lcm-gen`.

## Development

```bash
uv sync
uv run pre-commit install
uv run pytest
uv run ruff check .
```

The tests import every generated type, round-trip it through encode/decode, and compare all fingerprints with `tests/fingerprints.json`. A fingerprint change means a wire-format change. After intentionally changing a `.lcm` file, regenerate the file and commit it with the change:

```bash
UPDATE_FINGERPRINTS=1 uv run pytest
```

## Releases

[python-semantic-release](https://python-semantic-release.readthedocs.io/) runs in CI after tests pass. It derives the version from [conventional commits](https://www.conventionalcommits.org/), updates `pyproject.toml`, `uv.lock` and `CHANGELOG.md`, tags the release and creates a GitHub release with the wheel and sdist. Pushes to `main` make releases and pushes to `develop` make `-rc.N` prereleases.

## History

This repository was split out of the MOLARS repository (`lcm/` on `main` at `40170cb`) with its history preserved.
