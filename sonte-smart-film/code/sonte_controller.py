#!/usr/bin/env python3
"""
Sonte Smart Film RF Controller
Unified Python controller for smart film commands based on reverse-engineered RF protocol.

Usage (CLI):
    python sonte_controller.py button1    # Make film transparent
    python sonte_controller.py button2    # Make film opaque

Usage (module):
    from sonte_controller import SonteController
    ctrl = SonteController()
    ctrl.send_command('button1')
    ctrl.close()

RF Parameters:
    Frequency:      433.916 MHz
    Modulation:     ASK/OOK (Amplitude Shift Keying / On-Off Keying)
    Baud Rate:      2500 Hz
    Packet Length:  15-16 bits (varies by command)
    PWM Encoding:   1 -> '1000' (long high pulse), 0 -> '1110' (long high + short low)

Norwegian Comments:
    Fullstendig PWM key = Complete PWM key
    Fjernkontrollens key = The remote control's key
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

class SonteController:
    """Controller for Sonte smart film RF commands using RfCat."""

    def __init__(self):
        """Initialize RfCat connection and configure radio parameters."""
        self.d = RfCat()
        self._configure_radio()

        # Command definitions: raw byte payload, packet length, and repeat count
        # Fjernkontrollens kommandoer (Remote control's commands)
        self.commands = {
            'button1': {
                'key': '1111111110111011111100111',
                'data': b'\x88\x88\x88\x88\xe8\x88\xe8\x88\x88\x88\x8e\x88\x00\x00\x00\x88\x88\x88\x88\x8e\x88\x8e\x88\x88\x88\x88\xe8\x80\x00\x00\x00\x88\x88\x88\x88\x8e\x88\x8e\x88\x88\x88\x88\xe8\x80\x00\x00\x00\x88\x88\x88\x88\x8e\x88\x8e\x88\x88\x88\x88\xe8\x80\x00\x00\x00\x88\x88\x88\x88\x8e\x88\x8e\x88\x88\x88\x88\xe8\x80\x00\x00\x00',
                'pktlen': 15,
                'repeats': 1
            },
            'button2': {
                'key': '111111110111011111111101',
                'data': b'\x88\x88\x88\x88\xe8\x88\xe8\x88\x88\x88\x88\xe8\x00\x00\x00\x88\x88\x88\x88\x8e\x88\x8e\x88\x88\x88\x88\x8e\x80\x00\x00\x00\x88\x88\x88\x88\x8e\x88\x8e\x88\x88\x88\x88\x8e\x80\x00\x00\x00\x88\x88\x88\x88\x8e\x88\x8e\x88\x88\x88\x88\x8e\x80\x00\x00\x00\x88\x88\x88\x88\x8e\x88\x8e\x88\x88\x88\x88\x8e\x80\x00\x00\x00',
                'pktlen': 16,
                'repeats': 1
            }
        }

    def _configure_radio(self):
        """Configure RfCat radio settings for Sonte protocol."""
        self.d.setMdmModulation(MOD_ASK_OOK)
        self.d.setMdmDRate(2500)      # Baud rate 2500 Hz
        self.d.setMdmSyncMode(0)      # Disable preamble
        self.d.setFreq(433_916_000)   # 433.916 MHz
        self.d.setMaxPower()

    def send_command(self, command: str) -> bool:
        """
        Send a single command to the Sonte smart film.

        Args:
            command: One of 'button1', 'button2'.

        Returns:
            True if successful, False otherwise.
        """
        if command not in self.commands:
            print(f"Error: Unknown command '{command}'")
            print(f"Available: {', '.join(self.commands.keys())}")
            return False

        cmd_data = self.commands[command]
        payload = cmd_data['data']
        pktlen = cmd_data['pktlen']
        repeats = cmd_data['repeats']

        print(f"Sending '{command}' command...")
        print(f"Binary key: {cmd_data['key']}")

        try:
            # Set packet length for this specific command
            self.d.makePktFLEN(pktlen)

            # Send the command
            for _ in range(repeats):
                self.d.RFxmit(payload)
                sleep(0.01)

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
    controller = SonteController()
    success = controller.send_command(cmd)
    controller.close()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
