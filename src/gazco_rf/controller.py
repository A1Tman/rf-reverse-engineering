#!/usr/bin/env python3
"""
Gazco Fireplace RF Controller
Unified Python package for all fireplace commands based on reverse-engineered RF protocol.

Usage (module):
    from gazco_rf.controller import GazcoController
    ctrl = GazcoController()
    ctrl.send_command('on')
    ctrl.close()

Usage (CLI):
    gazco_on
    gazco_off
    gazco_up
    gazco_down

RF Parameters:
    Frequency:      433.876 MHz
    Modulation:     ASK/OOK (Amplitude Shift Keying / On-Off Keying)
    Symbol Rate:    ~1095 symbols/second
    Packet Length:  23 bits
    PWM Encoding:   1 -> '100' (short pulse), 0 -> '110' (long pulse)
    Inter-Packet Delay: 50 ms
"""

import sys
from time import sleep

# Import RfCat from the RFcat package (provides the rflib module)
try:
    import rflib
    RfCat = rflib.RfCat
    MOD_ASK_OOK = rflib.MOD_ASK_OOK
except ImportError as e:
    raise ModuleNotFoundError(
        "Could not import rflib: ensure the RFcat package is installed (pip install rfcat)"
    ) from e

class GazcoController:
    """Controller for Gazco fireplace RF commands using RfCat."""

    def __init__(self):
        """Initialize RfCat connection and configure radio parameters."""
        self.d = RfCat()
        self._configure_radio()

        # Command definitions: raw byte payload and repeat count
        self.commands = {
            'on':   {'data': b'\x9bm\xa4\x9aI\xb4\xdbI\xb0', 'repeats': 9},
            'off':  {'data': b'\x9bm\xa4\x9aI\xb4\xdbM\xb0', 'repeats': 10},
            'up':   {'data': b'\x9bm\xa4\x9aI\xb4\xdbi\xb0', 'repeats': 10},
            'down': {'data': b'\x9bm\xa4\x9aI\xb4\xdbm0', 'repeats': 19}
        }

    def _configure_radio(self):
        """Configure RfCat radio settings for Gazco protocol."""
        self.d.setMdmModulation(MOD_ASK_OOK)
        self.d.makePktFLEN(23)
        self.d.setMdmDRate(1095)      # Symbol rate matched to analysis
        self.d.setMdmSyncMode(0)      # No preamble
        self.d.setFreq(433_876_000)   # 433.876 MHz
        self.d.setMaxPower()

    def send_command(self, command: str) -> bool:
        """
        Send a single command to the Gazco fireplace.

        Args:
            command: One of 'on', 'off', 'up', 'down'.

        Returns:
            True if successful, False otherwise.
        """
        if command not in self.commands:
            print(f"Error: Unknown command '{command}'")
            print(f"Available: {', '.join(self.commands.keys())}")
            return False

        payload = self.commands[command]['data']
        repeats = self.commands[command]['repeats']
        print(f"Sending '{command}' ({repeats} repeats)...")

        try:
            for _ in range(repeats):
                self.d.RFxmit(payload)
                sleep(0.05)  # 50 ms inter-packet delay
            print(f"Command '{command}' sent successfully.")
            return True
        except Exception as e:
            print(f"Error sending '{command}': {e}")
            return False

    def close(self):
        """Cleanup and set radio to idle."""
        try:
            self.d.setModeIDLE()
        except Exception:
            pass


def main():
    """CLI entry point: parse args and send command."""
    if len(sys.argv) != 2 or sys.argv[1] in ('-h', '--help', 'help'):
        print(__doc__)
        sys.exit(0 if len(sys.argv) == 2 else 1)

    cmd = sys.argv[1].lower()
    controller = GazcoController()
    success = controller.send_command(cmd)
    controller.close()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
