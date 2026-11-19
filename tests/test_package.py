"""
Tests for the generated molars_lcmtypes package.

Fingerprints are pinned in fingerprints.json so any wire-format change is
deliberate. After intentionally changing a .lcm file, regenerate it with:

    UPDATE_FINGERPRINTS=1 uv run pytest
"""

import importlib
import json
import os
import pkgutil
import re
from pathlib import Path

import pytest

import hatch_build
import molars_lcmtypes

FINGERPRINTS = Path(__file__).with_name("fingerprints.json")
PACKAGE_DIR = Path(molars_lcmtypes.__file__).parent


def lcm_types() -> dict[str, type]:
    """All generated LCM classes keyed by LCM name (e.g. nav_server.msg.waypoint)."""
    found = {}
    for info in pkgutil.walk_packages(molars_lcmtypes.__path__, "molars_lcmtypes."):
        module = importlib.import_module(info.name)
        for value in vars(module).values():
            if isinstance(value, type) and hasattr(value, "_get_packed_fingerprint") and value.__module__ == info.name:
                found[info.name.removeprefix("molars_lcmtypes.")] = value
    return found


TYPES = lcm_types()


def test_all_lcm_sources_generated():
    sources = list(Path(hatch_build.__file__).parent.rglob("*.lcm"))
    assert len(TYPES) == len(sources) > 0


@pytest.mark.parametrize("name", sorted(TYPES))
def test_default_message_round_trips(name):
    cls = TYPES[name]
    encoded = cls().encode()
    assert cls.decode(encoded).encode() == encoded


def test_compas_references_point_at_compas_lcmtypes():
    stale = re.compile(r"molars_lcmtypes\.(stdlcm|senlcm|navlcm|geolcm)\b")
    offenders = [str(p) for p in PACKAGE_DIR.rglob("*.py") if stale.search(p.read_text())]
    assert offenders == []


def test_fingerprints_unchanged():
    current = {name: cls._get_packed_fingerprint().hex() for name, cls in sorted(TYPES.items())}
    if os.environ.get("UPDATE_FINGERPRINTS"):
        FINGERPRINTS.write_text(json.dumps(current, indent=2) + "\n")
    assert current == json.loads(FINGERPRINTS.read_text())


def test_rewrite_compas_references(tmp_path):
    module = tmp_path / "m.py"
    module.write_text(
        "import molars_lcmtypes.geolcm\n"
        "import molars_lcmtypes.nav_server.msg\n"
        "x = molars_lcmtypes.stdlcm.header_t()\n"
        "y = molars_lcmtypes.geolcmx\n"
    )
    assert hatch_build.rewrite_compas_references(tmp_path) == 1
    assert module.read_text() == (
        "import compas_lcmtypes.geolcm\n"
        "import molars_lcmtypes.nav_server.msg\n"
        "x = compas_lcmtypes.stdlcm.header_t()\n"
        "y = molars_lcmtypes.geolcmx\n"
    )
