# Gazco Fireplace RF Protocol

**Reverse engineering and implementation of the Gazco G6R fireplace remote control RF protocol.**

[![RF Frequency](https://img.shields.io/badge/RF-433.876%20MHz-green.svg)]()
[![Protocol](https://img.shields.io/badge/Protocol-23--bit%20PWM-blue.svg)]()

## Overview

This project documents the author's Gazco fireplace remote experiments at
433.876 MHz and the preserved Python implementation. The recorded commands
contain 23 logical bits encoded as PWM. Their proposed field meanings remain
hypotheses; the implementation submits the complete saved patterns.

**Documentation Note**: The RF analysis workflow screenshots referenced in the [methodology](../methodology/) directory are from a parallel RF project (Sonte smart film at 433.916 MHz) conducted in February 2019. The Gazco analysis was performed earlier (2017-2018) before systematic documentation practices were established. However, the methodology, tools, and process were identical - only the frequency and protocol-specific parameters differ between projects.

## Preserved transmissions

The controller and individual scripts now use identical recorded bursts from
`code/gazco_profiles.py`. The defaults preserve the standalone scripts. The
explicit `down_notes_19` variant retains the earlier note's nineteen repetitions;
`down` still uses ten. ON retains seven trailing zero bytes, although the earlier
note lists six. See [provenance and limitations](../TRANSMISSIONS.md).

## Technical Specifications

| Parameter | Value |
|-----------|-------|
| **Frequency** | 433.876 MHz (433.87 MHz) |
| **Modulation** | ASK/OOK (On-Off Keying) |
| **Encoding** | PWM (Pulse Width Modulation) |
| **PWM Mapping** | 1='100', 0='110' |
| **Decoded command length** | 23 logical bits; separate from the RFcat FLEN byte setting |
| **Data-rate setting** | 1095 symbols/s |
| **Historical timing notes** | Short/long high pulses roughly 300/600 samples at 320 kHz; shortest measured pulse 292 samples |
| **Inter-frame gaps** | Preserved in recorded frame bytes and padding; no host-side sleeps |

## Command Protocol

### Discovered Commands

All commands follow a consistent 23-bit structure with different trailing bits to distinguish button functions.

| Command | Binary Pattern | Encoded logical command (not the complete burst) | Recorded frames |
|---------|---------------|----------------|---------|
| **ON** | `10000011101110010001100` | `\x9bm\xa4\x9aI\xb4\xdbI\xb0` | 9 |
| **OFF** | `10000011101110010001000` | `\x9bm\xa4\x9aI\xb4\xdbM\xb0` | 10 |
| **UP** | `10000011101110010000100` | `\x9bm\xa4\x9aI\xb4\xdbi\xb0` | 10 |
| **DOWN** | `10000011101110010000010` | `\x9bm\xa4\x9aI\xb4\xdbm0` | 10 by default; 19 with `down_notes_19` |

### Protocol Analysis

**Proposed field interpretation** (23 bits; not confirmed):
```
Preamble: 1000001 (7 bits)
Address:  1101110010 (10 bits)
Command:  000XXX (6 bits)
```

The shared prefix and different suffixes are observed in these four patterns.
Their interpretation as preamble/address/command was not verified.

**Varying suffix** (last 6 bits):
- ON:   `001100`
- OFF:  `001000`
- UP:   `000100`
- DOWN: `000010`

### PWM Encoding Details

The protocol uses a simple PWM encoding scheme where binary data is converted to pulse patterns:

```
Binary '1' → PWM '100' → Short pulse + pause
Binary '0' → PWM '110' → Long pulse + pause

At the preserved 1095 symbols/s setting:
  One high/low unit: approximately 0.913 ms
  '1': high for one unit, low for two units
  '0': high for two units, low for one unit
```

**Example - UP Button**:
```
Binary:     10000011101110010000100
PWM:        100110110110110110100100100110100100100110110100110110110110100110110
Bytestring: \x9bm\xa4\x9aI\xb4\xdbi\xb0
```

This is the byte-aligned encoding of the logical key. The complete recorded
UP/DOWN frames also retain an additional `b0` and zero padding. Use the full
profiles described in the [protocol reference](../analysis/protocol_docs/PROTOCOL.md),
not this excerpt, when comparing transmit bytes.

## Hardware Requirements

### For Control (Minimum)
- **RfCat compatible device**: YARD Stick One, cc1111-based USB dongle
- **Target device**: Gazco fireplace with G6R remote system
- **Computer**: Any system supporting Python 3.10+ and RfCat

### For Analysis (Optional)
- **SDR Receiver**: RTL-SDR, HackRF, or similar
- **Antenna**: Tuned for 433 MHz
- **Analysis Software**: GNU Radio, Audacity, SDR#

## Installation

### Prerequisites

The [public quick start](../README.md#quick-start) needs no hardware or external
packages for dry runs and tests. For actual transmissions, follow the separate
[radio setup](../README.md#radio-access-for-maintainers). The import is named
`rflib`; do not install an unrelated package by that name.

### Verify RfCat Connection
```bash
# Test RfCat device
python -c "import rflib; d = rflib.RfCat(); print('RfCat connected:', d.getFreq())"
```

## Usage

### Command Line Interface

Individual command scripts for quick control:

```bash
# Navigate to code directory
cd code/scripts

# Control commands
python gazco_on.py      # Turn fireplace ON
python gazco_off.py     # Turn fireplace OFF
python gazco_up.py      # Increase temperature
python gazco_down.py    # Decrease temperature
```

### Programmatic Control

From `gazco-fireplace/code`, use the unified controller class for integration:

```python
from controller import GazcoController

controller = GazcoController()  # Opens hardware only for a valid actual send.
if not controller.send_command('on'):
    raise RuntimeError('Gazco transmission could not be submitted')
```

Each send attempts IDLE cleanup. A successful return means the recorded burst
was submitted, not that the fireplace acknowledged or acted on it.

### Inspect the exact waveform

From the repository root:

<!-- offline-smoke -->
```bash
python gazco-fireplace/code/controller.py on --dry-run
python gazco-fireplace/code/controller.py down_notes_19 --dry-run
```

The 1095 baud rate, padding, and frame repetitions are preserved. A complete
burst is submitted in one call; do not replace its embedded gaps with host-side
sleep calls. `down_notes_19` is a 304-byte alternative, not a new default.

## Code Structure

```
gazco-fireplace/
├── README.md              # This file
├── buttons.txt            # Raw protocol analysis data
└── code/
    ├── __init__.py
    ├── controller.py      # Controller and CLI
    ├── gazco_profiles.py  # Shared immutable recorded bursts
    ├── scripts/           # Individual command scripts
    │   ├── __init__.py
    │   ├── gazco_on.py    # ON command
    │   ├── gazco_off.py   # OFF command
    │   ├── gazco_up.py    # UP command
    │   └── gazco_down.py  # DOWN command
    └── utils/
        ├── __init__.py
        └── convert_gazco.py  # PWM conversion utilities
```

## Reverse Engineering Process

The author's historical account follows the methodology documented in the
[methodology](../methodology/) directory. These steps describe the earlier
experiments, not new hardware tests of the current revision:

1. **Frequency Discovery**: Located 433.876 MHz carrier using SDR receiver
2. **Signal Capture**: Recorded raw button presses with HDSDR
3. **Demodulation**: Extracted ASK/OOK envelope and analyzed timing
4. **PWM Analysis**: Identified 1='100', 0='110' encoding pattern
5. **Protocol Extraction**: Decoded 23-bit command structure from timing data
6. **Implementation**: Created Python RfCat controller
7. **Validation**: Tested all commands with physical fireplace

### Analysis Data

The [buttons.txt](buttons.txt) file contains the raw analysis output from the signal processing phase:

```
Gazco button up:
bin: 10000011101110010000100
PWM Key: 100110110110110110100100100110100100100110110100110110110110100110110
Bytestring: \x9bm\xa4\x9aI\xb4\xdbi\xb0

Gazco frequency: 433.87 MHz
1=300 samples
0=600 samples
pause=300 samples
```

## Testing & Validation

Run `python -m unittest discover -s tests -v` from the repository root.
Hardware-free tests compare every controller and wrapper transmission against
frozen source bytes, radio settings, and hashes. They also verify failure
reporting, cleanup, and harmless imports/help/dry runs.

No new physical-device or range tests were performed. Earlier hardware-testing
claims in this documentation are not independently verified. The original
notes remain preserved, including the unresolved ON and DOWN discrepancies.

## Troubleshooting

### Device Not Responding

**Check RfCat Configuration**:
```python
import rflib
d = rflib.RfCat()
frequency, register_hex = d.getFreq()
print(f"Frequency: {frequency} Hz")        # Compare with the selected profile.
print(f"Modulation: {d.getMdmModulation()}") # Should be MOD_ASK_OOK
print(f"Data Rate: {d.getMdmDRate()}")      # Should be ~1095
```

**Common Issues**:
- Frequency drift: Verify 433.876 MHz exactly
- Insufficient power: Check RfCat transmission power settings
- Timing errors: Ensure baud rate is correct
- Repetition differences: Check the selected recorded profile and the documented ten/nineteen-frame DOWN alternatives in [TRANSMISSIONS.md](../TRANSMISSIONS.md).

### Interference Issues

The 433 MHz band is crowded with many devices:
- Weather stations
- Garage door openers
- Wireless sensors
- Other remote controls

**Solutions**:
- Test in different location
- Compare a new capture with the selected preserved burst before changing it
- Record failed submissions and observed target responses separately
- Verify frequency accuracy

## Safety Considerations

**IMPORTANT - Read Before Use**:

This project controls gas fireplace equipment, which presents potential safety hazards if misused.

### Safety Requirements

1. **Supervision**: Never operate fireplace remotely without visual confirmation
2. **Ventilation**: Ensure proper ventilation per manufacturer guidelines
3. **Testing**: Thoroughly test in safe conditions before regular use
4. **Backup Control**: Maintain manual remote as primary control method
5. **Carbon Monoxide**: Install and maintain CO detectors
6. **Emergency Shutoff**: Know location of gas shutoff valve

### Responsible Use

- Only use on devices you own
- Follow all manufacturer safety guidelines
- Do not automate unattended operation
- Maintain fireplace per manufacturer schedule
- Consult professional for any safety concerns

## Legal Compliance

### Radio Regulations

Check the applicable frequency, power, duty-cycle, and equipment requirements
for your location. The historical device reports and saved controller settings
do not certify a new transmitter or establish compliance for another setup.

### Intellectual Property

This reverse engineering was conducted for:
- Educational purposes
- Personal use on owned equipment
- Research and documentation

No manufacturer trade secrets were obtained improperly. All analysis was performed on legally purchased equipment using publicly observable RF emissions.

## Related Documentation

- **[Main README](../README.md)**: Repository overview and project comparison
- **[Methodology](../methodology/README.md)**: Detailed reverse engineering process
- **[Sonte Project](../sonte-smart-film/README.md)**: Parallel RF project with analysis screenshots

## Future Enhancements

Potential improvements for this project:

- [ ] Home automation integration (Home Assistant, OpenHAB)
- [ ] Temperature sensing feedback loop
- [ ] Scheduling and timer functionality
- [ ] Voice control integration
- [ ] Web API for remote control
- [ ] Security improvements (replay attack prevention)

**Note**: Any automation should maintain safety considerations listed above.

## References

- **FCC Test Report**: See [docs/FCC_TEST_REPORT.pdf](../docs/FCC_TEST_REPORT.pdf)
- **Device Manual**: See [docs/GV60_MANUAL.pdf](../docs/GV60_MANUAL.pdf)
- **RfCat Documentation**: [github.com/atlas0fd00m/rfcat](https://github.com/atlas0fd00m/rfcat)
- **ISM Band Information**: [Wikipedia - ISM Band](https://en.wikipedia.org/wiki/ISM_band)

## License

This project is licensed under the MIT License - see the [LICENSE.md](../LICENSE.md) file for details.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

---

**Project Status**: Recorded profiles preserved; new hardware validation pending.

**Last Updated**: 2024 (documentation)
