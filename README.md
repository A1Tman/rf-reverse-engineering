# RF Reverse Engineering Projects

**Systematic reverse engineering of 433 MHz ISM band remote control protocols using Software Defined Radio (SDR) techniques.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![RF Frequency](https://img.shields.io/badge/RF-433%20MHz%20ISM-green.svg)]()

## Overview

This repository documents two independent RF protocol reverse engineering projects conducted between 2017-2019.

### Projects

| Project | Frequency | Protocol |
|---------|-----------|----------|
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
require RfCat. The maintainer's private Python 3 fork reports firmware errors;
older releases may discard those errors internally.

## Quick Start

### Explore without hardware

Use Python 3.11 or newer. Clone this public repository and optionally create a
virtual environment. The controller dry runs and regression tests need only
the Python standard library; no private checkout or dependency installation is
required.

```bash
git clone https://github.com/A1Tman/rf-reverse-engineering.git
cd rf-reverse-engineering
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
```

Run from the repository root:

<!-- offline-smoke -->
```bash
python gazco-fireplace/code/controller.py on --dry-run
python sonte-smart-film/code/sonte_controller.py original --dry-run
```

```bash
python -m unittest discover -s tests -v
python tools/check_documentation.py
```

Dry runs print full recorded bytes and settings. Tests compare the profiles
against independent frozen fixtures and check failure handling with fake radios.
The optional analysis utilities use `bitstring` 4.x, matching the maintained
radio and RF_Projects environments. Install their requirements separately:

```bash
python -m pip install -r requirements.txt
python gazco-fireplace/code/utils/convert_gazco.py
python sonte-smart-film/code/sonte_signal_analyzer.py
python tools/check_converters.py
```

### Radio access for maintainers

Actual transmission needs an RfCat-compatible dongle (such as YARD Stick One),
the relevant target device, and a compatible RfCat installation. Raw waveform
analysis also needs an SDR receiver and its recording software.

The maintained [rfcat_py3 repository](https://github.com/A1Tman/rfcat_py3) is
private. With access, place its reviewed checkout beside this repository and
install that source directly:

```bash
python -m pip install -e "../rfcat_py3[hardware]"
```

`requirements.txt` contains only the optional offline converter dependency;
it does not install or replace RfCat. The maintained checkout is the documented
live-radio path. The shared sender retains legacy `None` return-value handling,
but that compatibility cannot recover firmware statuses an older library
discarded. See [compatibility and validation limits](TRANSMISSIONS.md#inspect-and-test-without-hardware).

### Usage

Run these from the repository root only after setting up radio access. These
commands send real transmissions; append `--dry-run` to inspect them instead.

**Gazco Fireplace Control:**
```bash
python gazco-fireplace/code/controller.py on
python gazco-fireplace/code/controller.py off
python gazco-fireplace/code/controller.py up
python gazco-fireplace/code/controller.py down
```

**Sonte Smart Film Control:**
```bash
python sonte-smart-film/code/sonte_controller.py button1    # Historical transparent label
python sonte-smart-film/code/sonte_controller.py button2    # Historical opaque label
```

## Project Comparison

| Specification | Gazco Fireplace | Sonte Smart Film |
|--------------|-----------------|------------------|
| **Frequency** | 433.876 MHz | 433.916 MHz |
| **Modulation** | ASK/OOK | ASK/OOK |
| **Bit Length** | 23 bits | 24-25 bits |
| **PWM Encoding** | 1='100', 0='110' | 1='1000', 0='1110' |
| **Data-rate setting** | 1095 symbols/s | 2500 symbols/s |
| **Timing rationale** | Shortest pulse: 292 samples at 320 kHz | Four encoded units per logical bit |
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
- **Languages**: Python 3.11+

## Legal & Safety

**Important Disclaimers:**
- This project is for **educational and research purposes only**
- Only use on devices you own or have explicit permission to control
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
