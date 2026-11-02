#!/usr/bin/env python3
"""Gazco DOWN: the shared standalone-script transmission profile."""

from pathlib import Path
import sys

_CODE = str(Path(__file__).resolve().parents[1])
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)
from controller import main

if __name__ == '__main__':
    raise SystemExit(main(default_command='down'))
