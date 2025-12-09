# Gazco Fireplace RF Protocol

**Reverse engineering and implementation of the Gazco G6R fireplace remote control RF protocol.**

[![RF Frequency](https://img.shields.io/badge/RF-433.876%20MHz-green.svg)]()
[![Protocol](https://img.shields.io/badge/Protocol-23--bit%20PWM-blue.svg)]()

## Overview

This project documents the complete reverse engineering of the Gazco fireplace remote control system operating at 433.876 MHz. The analysis revealed a 23-bit command structure using PWM encoding, which has been successfully reimplemented using RfCat for programmatic control.

**Documentation Note**: The RF analysis workflow screenshots referenced in the [methodology](../methodology/) directory are from a parallel RF project (Sonte smart film at 433.916 MHz) conducted in February 2019. The Gazco analysis was performed earlier (2017-2018) before systematic documentation practices were established. However, the methodology, tools, and process were identical - only the frequency and protocol-specific parameters differ between projects.

## Technical Specifications

| Parameter | Value |
|-----------|-------|
| **Frequency** | 433.876 MHz (433.87 MHz) |
| **Modulation** | ASK/OOK (On-Off Keying) |
| **Encoding** | PWM (Pulse Width Modulation) |
| **PWM Mapping** | 1='100', 0='110' |
| **Packet Length** | 23 bits |
| **Baud Rate** | 1095 Hz |
| **Sample Timing** | 1=300 samples, 0=600 samples @ 320kHz |
| **Pause Duration** | 300 samples |

## Command Protocol

### Discovered Commands

All commands follow a consistent 23-bit structure with different trailing bits to distinguish button functions.

| Command | Binary Pattern | PWM Bytestring | Repeats |
|---------|---------------|----------------|---------|
| **ON** | `10000011101110010001100` | `\x9bm\xa4\x9aI\xb4\xdbI\xb0` | 9 |
| **OFF** | `10000011101110010001000` | `\x9bm\xa4\x9aI\xb4\xdbM\xb0` | 10 |
| **UP** | `10000011101110010000100` | `\x9bm\xa4\x9aI\xb4\xdbi\xb0` | 10 |
| **DOWN** | `10000011101110010000010` | `\x9bm\xa4\x9aI\xb4\xdbm0` | 19 |

### Protocol Analysis

**Packet Structure** (23 bits):
```
Preamble: 1000001 (7 bits)
Address:  1101110010 (10 bits)
Command:  000XXX (6 bits)
```

**Command Bits** (last 6 bits):
- ON:   `001100`
- OFF:  `001000`
- UP:   `000100`
- DOWN: `000010`

### PWM Encoding Details

The protocol uses a simple PWM encoding scheme where binary data is converted to pulse patterns:

```
Binary '1' → PWM '100' → Short pulse + pause
Binary '0' → PWM '110' → Long pulse + pause

Timing (at 320 kHz sampling):
  '1' pulse:  300 samples (~0.94 ms)
  '0' pulse:  600 samples (~1.88 ms)
  Pause:      300 samples (~0.94 ms)
```

**Example - UP Button**:
```
Binary:     10000011101110010000100
PWM:        100110110110110110100100100110100100100110110100110110110110100110110
Bytestring: \x9bm\xa4\x9aI\xb4\xdbi\xb0
```

## Hardware Requirements

### For Control (Minimum)
- **RfCat compatible device**: YARD Stick One, cc1111-based USB dongle
- **Target device**: Gazco fireplace with G6R remote system
- **Computer**: Any system supporting Python 3.6+ and RfCat

### For Analysis (Optional)
- **SDR Receiver**: RTL-SDR, HackRF, or similar
- **Antenna**: Tuned for 433 MHz
- **Analysis Software**: GNU Radio, Audacity, SDR#

## Installation

### Prerequisites
```bash
# Install RfCat library
pip install rflib

# Clone repository
git clone https://github.com/A1Tman/rf-reverse-engineering.git
cd rf-reverse-engineering/gazco-fireplace
```

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

Use the unified controller class for integration:

```python
from controller import GazcoController

# Initialize controller
controller = GazcoController()

# Send commands
controller.send_command('on')      # Power on
time.sleep(1)
controller.send_command('up')      # Increase temp
time.sleep(1)
controller.send_command('off')     # Power off

# Clean up
controller.close()
```

### Advanced Usage

Direct binary command transmission:

```python
import rflib
import time

# Initialize RfCat
d = rflib.RfCat()

# Configure radio parameters
d.setFreq(433876000)               # 433.876 MHz
d.setMdmModulation(rflib.MOD_ASK_OOK)
d.setMdmDRate(3100)                # Baud rate
d.makePktFLEN(23)                  # 23-bit packets

# Define command (UP button)
cmd_binary = '10000011101110010000100'
cmd_pwm = convert_to_pwm(cmd_binary)  # Convert using PWM rules

# Transmit with repetitions
for _ in range(10):
    d.RFxmit(cmd_pwm)
    time.sleep(0.01)

# Clean up
d.setModeIDLE()
```

## Code Structure

```
gazco-fireplace/
├── README.md              # This file
├── buttons.txt            # Raw protocol analysis data
└── code/
    ├── __init__.py
    ├── controller.py      # Main unified controller class
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

The analysis followed the standard RF reverse engineering methodology documented in the [methodology](../methodology/) directory:

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

The implementation has been validated through:

- ✅ **Functional Testing**: All four commands operate correctly
- ✅ **Timing Verification**: PWM timing matches original remote
- ✅ **Repetition Testing**: Correct number of packet repeats
- ✅ **Range Testing**: Performance matches manufacturer specifications
- ✅ **Interference Analysis**: No issues in typical 433 MHz environments

### Test Procedure

1. Power on fireplace manually
2. Test ON command - verify ignition
3. Test UP command - observe temperature increase
4. Test DOWN command - observe temperature decrease
5. Test OFF command - verify shutdown
6. Measure response time and reliability

## Troubleshooting

### Device Not Responding

**Check RfCat Configuration**:
```python
d = rflib.RfCat()
print(f"Frequency: {d.getFreq()}")          # Should be 433876000
print(f"Modulation: {d.getMdmModulation()}") # Should be MOD_ASK_OOK
print(f"Data Rate: {d.getMdmDRate()}")      # Should be ~3100
```

**Common Issues**:
- Frequency drift: Verify 433.876 MHz exactly
- Insufficient power: Check RfCat transmission power settings
- Timing errors: Ensure baud rate is correct
- Missing repeats: Commands require 9-19 repetitions

### Interference Issues

The 433 MHz band is crowded with many devices:
- Weather stations
- Garage door openers
- Wireless sensors
- Other remote controls

**Solutions**:
- Test in different location
- Increase packet repetitions
- Add error detection logic
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

**FCC Part 15 (United States)**:
- 433 MHz ISM band operation permitted
- Low power unlicensed operation
- No harmful interference to licensed services

**Similar regulations apply in other jurisdictions** - verify local requirements.

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

**Project Status**: ✅ Complete and functional (2017-2018)

**Last Updated**: 2024 (documentation)
