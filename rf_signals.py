"""Shared, hardware-lazy execution of immutable recorded RF transmissions."""

import argparse
from dataclasses import dataclass
from numbers import Integral
import sys


@dataclass(frozen=True)
class Transmission:
    data: bytes
    frequency: int
    baud: int
    packet_length: int
    source: str


def transmit(profile, radio, modulation):
    """Send one unchanged recorded burst and idle on success or failure."""
    completed = False
    try:
        radio.setMdmModulation(modulation)
        radio.makePktFLEN(profile.packet_length)
        radio.setMdmDRate(profile.baud)
        radio.setMdmSyncMode(0)
        radio.setFreq(profile.frequency)
        radio.setMaxPower()
        # Repetition and gaps are already encoded in data. In particular the
        # 304-byte notes variant must use RFxmit's long-payload path, no repeat.
        status = radio.RFxmit(profile.data)
        if status is not None and (not isinstance(status, Integral) or status != 0):
            raise RuntimeError(f"RF transmission failed with status {status!r}.")
        completed = True
    finally:
        try:
            radio.setModeIDLE()
        except Exception as error:
            if completed:
                raise
            print(f"Could not idle radio after failure: {error}", file=sys.stderr)


class RecordedController:
    """Controllers connect only when a valid command is actually sent."""

    profiles = None

    def __init__(self, radio=None, modulation=None):
        self.d = radio
        self._modulation = modulation
        self.commands = self.profiles

    def send_command(self, command):
        if command not in self.profiles:
            print(f"Unknown command {command!r}. Available: {', '.join(self.profiles)}", file=sys.stderr)
            return False
        try:
            if self.d is None:
                import rflib
                self._modulation = rflib.MOD_ASK_OOK
                self.d = rflib.RfCat()
            elif self._modulation is None:
                raise ValueError("Supply modulation when injecting a radio.")
            transmit(self.profiles[command], self.d, self._modulation)
        except Exception as error:
            print(f"Could not send {command!r}: {error}", file=sys.stderr)
            return False
        print(f"Transmission {command!r} submitted; target reception is not acknowledged.")
        return True

    def close(self):
        if self.d is not None:
            self.d.setModeIDLE()


def run_cli(controller_class, argv=None, default_command=None):
    parser = argparse.ArgumentParser(description="Send a preserved recorded RF burst.")
    parser.add_argument('command', choices=tuple(controller_class.profiles),
                        nargs='?' if default_command else None, default=default_command)
    parser.add_argument('--dry-run', action='store_true',
                        help='inspect bytes and settings without loading RfCat or opening a radio')
    args = parser.parse_args(argv)
    profile = controller_class.profiles[args.command]
    if args.dry_run:
        print(f"Command: {args.command}")
        print(f"Source: {profile.source}")
        print(f"Frequency: {profile.frequency} Hz; data rate: {profile.baud}; FLEN: {profile.packet_length}")
        print(f"Transmission: {len(profile.data)} bytes, one burst, no RFxmit repeat argument")
        print(f"Payload hex: {profile.data.hex()}")
        return 0
    try:
        return 0 if controller_class().send_command(args.command) else 1
    except KeyboardInterrupt:
        print("Stopped.", file=sys.stderr)
        return 130
