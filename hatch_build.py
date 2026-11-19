"""
Hatch build hook: generate the molars_lcmtypes Python package from the .lcm sources.

lcm-gen applies --package-prefix to every referenced type, so references to
CoMPAS types (stdlcm, senlcm, navlcm, geolcm) are rewritten afterwards to
import from the compas_lcmtypes package instead.
"""

import re
import shutil
import subprocess
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

PACKAGE_NAME = "molars_lcmtypes"
COMPAS_PACKAGE_NAME = "compas_lcmtypes"
COMPAS_LCM_PACKAGES = ("stdlcm", "senlcm", "navlcm", "geolcm")

_COMPAS_REF = re.compile(rf"\b{PACKAGE_NAME}\.({'|'.join(COMPAS_LCM_PACKAGES)})\b")


def rewrite_compas_references(package_dir: Path) -> int:
    """Point references to CoMPAS LCM packages at compas_lcmtypes. Returns files changed."""
    changed = 0
    for path in package_dir.rglob("*.py"):
        text = path.read_text()
        new_text = _COMPAS_REF.sub(rf"{COMPAS_PACKAGE_NAME}.\1", text)
        if new_text != text:
            path.write_text(new_text)
            changed += 1
    return changed


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        """Generate Python code from the LCM files before building."""
        root_dir = Path(self.root)
        package_dir = root_dir / PACKAGE_NAME
        lcm_files = sorted(str(p) for p in root_dir.rglob("*.lcm") if ".venv" not in p.parts)
        if not lcm_files:
            # Building a wheel from an sdist that already contains generated code
            if package_dir.exists():
                return
            raise RuntimeError("No .lcm files found")

        shutil.rmtree(package_dir, ignore_errors=True)
        cmd = ["lcm-gen", "--python", "--package-prefix", PACKAGE_NAME, "--ppath", str(root_dir), *lcm_files]
        self.app.display_info(f"Generating Python types from {len(lcm_files)} LCM files")
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            self.app.display_error(f"lcm-gen failed:\n{e.stdout}\n{e.stderr}")
            raise

        changed = rewrite_compas_references(package_dir)
        self.app.display_success(f"Generated {PACKAGE_NAME}; rewrote CoMPAS references in {changed} files")
