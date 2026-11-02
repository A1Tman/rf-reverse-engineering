#!/usr/bin/env python3
"""Gazco recorded transmissions. Construction/import never opens a radio."""

from pathlib import Path
import sys

# Support direct scripts and imports from this historical, non-packaged layout.
_ROOT = str(Path(__file__).resolve().parents[2])
_CODE = str(Path(__file__).resolve().parent)
for _path in (_ROOT, _CODE):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from rf_signals import RecordedController, run_cli
from gazco_profiles import PROFILES


class GazcoController(RecordedController):
    profiles = PROFILES


def main(argv=None, default_command=None):
    return run_cli(GazcoController, argv, default_command)


if __name__ == '__main__':
    raise SystemExit(main())
