"""Recorded bursts; see TRANSMISSIONS.md for provenance and unresolved differences."""

from types import MappingProxyType
from rf_signals import Transmission

PROFILES = MappingProxyType({
    'button1': Transmission(
        data=bytes.fromhex('88888888e888e88888888e88000000888888888e888e88888888e880000000888888888e888e88888888e880000000888888888e888e88888888e880000000888888888e888e88888888e880000000'),
        frequency=433916000, baud=2500, packet_length=15,
        source='43ef809:sonte-smart-film/code/sonte_button1_transparent.py (existing button label retained)',
    ),
    'button2': Transmission(
        data=bytes.fromhex('88888888e888e888888888e8000000888888888e888e888888888e80000000888888888e888e888888888e80000000888888888e888e888888888e80000000888888888e888e888888888e80000000'),
        frequency=433916000, baud=2500, packet_length=16,
        source='43ef809:sonte-smart-film/code/sonte_button2_opaque.py (existing button label retained)',
    ),
    'original': Transmission(
        data=bytes.fromhex('888888888e888e888888ee8880000000888888888e888e888888ee8880000000888888888e888e888888ee8880000000888888888e888e888888ee8880000000'),
        frequency=433916000, baud=2500, packet_length=16,
        source='RF_Projects 599a308:scripts/sonteremote.py; physical button meaning unassigned',
    ),
})
