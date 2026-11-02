# RF Reverse Engineering Projects

**Systematic reverse engineering of 433 MHz ISM band remote control protocols using Software Defined Radio (SDR) techniques.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![RF Frequency](https://img.shields.io/badge/RF-433%20MHz%20ISM-green.svg)]()

## Overview

This repository documents two independent RF protocol reverse engineering projects conducted between 2017-2019.

### Projects

| Project | Frequency | Protocol | Status |
|---------|-----------|----------|--------|
| [**Gazco Fireplace Remote**](gazco-fireplace/) | 433.876 MHz | 23-bit PWM (1='100', 0='110') |
| [**Sonte Smart Film Remote**](sonte-smart-film/) | 433.916 MHz | 24-25 bit PWM (1='1000', 0='1110') |

Both projects used identical analysis methodologies and tools, starting from unknown RF signals and ending with working Python implementations using RfCat.

## Methodology

The reverse engineering process follows a systematic approach documented in the [methodology](methodology/) directory:

```
[Unknown RF Signal]
        ↓
[1. Frequency Discovery]     → SDR# / HDSDR
        ↓
[2. Signal Capture]           → GNU Radio / Raw IQ samples
        ↓
[3. Demodulation]             → Audacity / Python analysis
        ↓
[4. Protocol Analysis]        → Binary pattern extraction
        ↓
[5. PWM Decoding]             → Timing analysis
        ↓
[6. Implementation]           → Python + RfCat
        ↓
[Working Controller]
```

### Key Techniques
- **Frequency identification** using SDR receivers and waterfall displays
- **Signal processing** with GNU Radio and audio analysis tools
- **PWM pattern recognition** through timing analysis
- **Protocol validation** via capture comparison
- **Practical implementation** using RfCat hardware

See the [Methodology README](methodology/README.md) for detailed documentation of the reverse engineering process.

## Recorded transmission profiles

Controllers and standalone scripts share the same preserved burst profiles.
Gazco defaults keep the standalone-script bytes and padding; `down_notes_19`
is a separate variant from the earlier notes. Sonte adds `original`, the
64-byte transmission from the 2024 script, without assigning it a button meaning.

See [Transmission provenance and unresolved differences](TRANSMISSIONS.md)
for the ON padding and DOWN repetition discrepancies. These changes have offline
byte-for-byte regression tests; no new hardware validation is claimed.

```bash
python gazco-fireplace/code/controller.py on --dry-run
python sonte-smart-film/code/sonte_controller.py original --dry-run
python -m unittest discover -s tests -v
```

Imports, construction, help and dry runs do not open a radio. Actual sends
require RfCat. The [maintained Python 3 fork](https://github.com/A1Tman/rfcat_py3)
reports firmware errors; older releases may discard those errors internally.

## Quick Start

### Hardware Requirements
- **RfCat compatible device** (YARD Stick One, cc1111-based USB dongle)
- **Target devices**: Gazco fireplace or Sonte smart film controller
- **Optional**: SDR receiver for signal analysis (RTL-SDR, HackRF, etc.)

### Installation

Use Python 3.10 or newer and the maintained local `rfcat_py3` checkout beside
this repository. Install that checkout first so the controller uses the version
that reports numeric firmware errors:

```bash
cd rf-reverse-engineering
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -e "../rfcat_py3[hardware]"
python -m pip install -r requirements.txt
```

The tested RfCat status changes may exist only on the local branch. Use the
existing sibling checkout; this setup does not assume those changes are already
published on GitHub. Installing a generic older `rfcat` release alone cannot
provide error statuses that its implementation discards. See
[compatibility notes](TRANSMISSIONS.md#inspect-and-test-without-hardware).

### Usage

**Gazco Fireplace Control:**
```bash
cd gazco-fireplace/code
python scripts/gazco_on.py    # Turn fireplace ON
python scripts/gazco_off.py   # Turn fireplace OFF
python scripts/gazco_up.py    # Increase temperature
python scripts/gazco_down.py  # Decrease temperature
```

**Sonte Smart Film Control:**
```bash
cd sonte-smart-film/code
python sonte_controller.py button1    # Make transparent
python sonte_controller.py button2    # Make opaque
```

## Project Comparison

| Specification | Gazco Fireplace | Sonte Smart Film |
|--------------|-----------------|------------------|
| **Frequency** | 433.876 MHz | 433.916 MHz |
| **Modulation** | ASK/OOK | ASK/OOK |
| **Bit Length** | 23 bits | 24-25 bits |
| **PWM Encoding** | 1='100', 0='110' | 1='1000', 0='1110' |
| **Baud Rate** | 1095 Hz | ~2500 Hz |
| **Sample Timing** | 1=300, 0=600 @ 320kHz | Different timing |
| **Commands** | ON/OFF/UP/DOWN | Transparent/Opaque |

## Repository Structure

```
rf-reverse-engineering/
├── README.md                           # This file
├── methodology/
│   ├── README.md                       # Detailed methodology documentation
│   └── screenshots/                    # Process workflow screenshots (from Sonte session)
├── gazco-fireplace/
│   ├── README.md                       # Gazco project documentation
│   ├── buttons.txt                     # Raw protocol analysis data
│   └── code/                           # Python implementation
│       ├── controller.py               # Main controller class
│       ├── scripts/                    # Individual command scripts
│       └── utils/                      # PWM conversion utilities
├── sonte-smart-film/
│   ├── README.md                       # Sonte project documentation
│   └── code/                           # Python implementation (Norwegian comments)
├── LICENSE.md                          # MIT License
└── CONTRIBUTING.md                     # Contribution guidelines
```

## Documentation

- **[Methodology](methodology/README.md)**: Complete RF reverse engineering process
- **[Gazco Project](gazco-fireplace/README.md)**: Fireplace remote control protocol
- **[Sonte Project](sonte-smart-film/README.md)**: Smart film remote control protocol

## Tools Used

- **SDR Software**: SDR#, HDSDR, GNU Radio
- **Analysis Tools**: Audacity, Python (numpy, matplotlib)
- **Hardware**: RfCat (YARD Stick One), RTL-SDR
- **Languages**: Python 3.10+

## Legal & Safety

**Important Disclaimers:**
- This project is for **educational and research purposes only**
- Only use on devices you own or have explicit permission to control
- Complies with local regulations for 433 MHz ISM band usage
- Transmission on 433 MHz ISM band must follow local power and duty cycle regulations
- No warranty provided - use at your own risk

**Safety Considerations:**
- Gazco project controls gas fireplace equipment - improper use could create safety hazards
- Always ensure proper ventilation and follow manufacturer safety guidelines
- Test in a safe environment with appropriate supervision

## Contributing

Contributions, issues, and feature requests are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

- **RfCat project** for the excellent RF analysis toolkit
- **GNU Radio community** for signal processing tools
- **RTL-SDR project** for affordable SDR hardware support

## Related Projects

- [RfCat](https://github.com/atlas0fd00m/rfcat) - RF analysis tool used in these projects
- [Universal Radio Hacker](https://github.com/jopohl/urh) - Excellent tool for RF protocol analysis
- [GNU Radio](https://www.gnuradio.org/) - Software radio toolkit

---

**Note**: Analysis timeline: Gazco project (2017-2018), Sonte project (February 2019). Workflow screenshots are from the Sonte analysis session, as systematic documentation practices were established by that time.
