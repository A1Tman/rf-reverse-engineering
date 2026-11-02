#!/usr/bin/env python3
"""Verify the optional analysis utilities against frozen pre-update outputs."""

import contextlib
import importlib.abc
import io
from pathlib import Path
import runpy
import sys


ROOT = Path(__file__).resolve().parents[1]
# Recorded with bitstring 4.2.3 before updating the optional dependency contract.
# These encoded keys are distinct from the complete transmit-profile bursts.
REFERENCES = (
    ('gazco-fireplace/code/utils/convert_gazco.py', 'erf_data',
     '9b6da49a49b4db6d30',
     '100110110110110110100100100110100100100110110100110110110110110100110'),
    ('sonte-smart-film/code/sonte_signal_analyzer.py', 'rf_data',
     '888888888e888e888888ee8880',
     '1000100010001000100010001000100010001110100010001000111010001000100010001000100011101110100010001000'),
)


class NoRadio(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in ('rflib', 'usb', 'serial'):
            raise ImportError('Radio access is forbidden in converter checks')


def main():
    blocker = NoRadio()
    sys.meta_path.insert(0, blocker)
    try:
        for relative, data_name, expected_hex, expected_pwm in REFERENCES:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = runpy.run_path(str(ROOT / relative), run_name='__main__')
            if result[data_name] != bytes.fromhex(expected_hex):
                raise AssertionError(f'{relative}: encoded bytes changed')
            if result['pwm_key'] != expected_pwm:
                raise AssertionError(f'{relative}: PWM sequence changed')
            if repr(bytes.fromhex(expected_hex)) not in output.getvalue():
                raise AssertionError(f'{relative}: byte output missing from CLI result')
            print(f'{relative}: {len(result[data_name])} encoded bytes verified')
    finally:
        sys.meta_path.remove(blocker)


if __name__ == '__main__':
    main()
