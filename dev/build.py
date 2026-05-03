#!/usr/bin/env python3
# Canonical build entry point — regenerates ui_*.py and resources_rc.py
# from .ui/.qrc sources. Excluded from any release zip via the `dev/`
# convention (mirrors dsviper-tools).
#
# Run from the repo root:
#
#     python3 dev/build.py
#
# Inputs (committed sources):
#   - resources.qrc
#   - dsviper_components/*.ui                    (shared component widgets)
#   - components/*.ui                       (graph-editor panels)
#   - select_graph_dialog.ui                (root-level app dialog)
#
# Outputs (committed; regeneration is reproducible thanks to PySide6
# pinned in requirements.txt):
#   - resources_rc.py                       (at repo root)
#   - dsviper_components/ui_*.py
#   - components/ui_*.py
#   - ui_select_graph_dialog.py             (at repo root)
#
# Idempotent: running twice on a clean tree leaves the tree clean.

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
QRC = REPO / "resources.qrc"
RCC_OUT = REPO / "resources_rc.py"
UI_DIRS = (REPO, REPO / "dsviper_components", REPO / "components")


def require(tool: str) -> str:
    path = shutil.which(tool)
    if not path:
        sys.exit(f"error: {tool} not found in PATH (install PySide6).")
    return path


def pyside6_version() -> str:
    try:
        import PySide6
    except ImportError:
        sys.exit("error: PySide6 not installed (pip install -r requirements.txt).")
    return PySide6.__version__


def regen_resources(rcc: str) -> None:
    if not QRC.is_file():
        sys.exit(f"error: missing {QRC.relative_to(REPO)}")
    print(f"  pyside6-rcc {QRC.name} -> {RCC_OUT.name}")
    subprocess.run([rcc, str(QRC), "-o", str(RCC_OUT)], check=True, cwd=REPO)


def regen_ui(uic: str) -> None:
    total = 0
    for ui_dir in UI_DIRS:
        # At repo root we only want top-level *.ui (not ones in subdirs);
        # subdirs are processed in their own iteration.
        if ui_dir == REPO:
            ui_files = sorted(p for p in ui_dir.glob("*.ui") if p.parent == REPO)
        else:
            ui_files = sorted(ui_dir.glob("*.ui"))
        for ui in ui_files:
            out = ui.with_name(f"ui_{ui.stem}.py")
            print(f"  pyside6-uic {ui.relative_to(REPO)} -> {out.relative_to(REPO)}")
            subprocess.run([uic, str(ui), "-o", str(out)], check=True, cwd=REPO)
            total += 1
    if total == 0:
        sys.exit("error: no *.ui files found")


def main() -> None:
    print(f"PySide6 {pyside6_version()}")
    rcc = require("pyside6-rcc")
    uic = require("pyside6-uic")
    print("Regenerating Qt resource module...")
    regen_resources(rcc)
    print("Regenerating UI modules...")
    regen_ui(uic)
    print("Done.")


if __name__ == "__main__":
    main()
