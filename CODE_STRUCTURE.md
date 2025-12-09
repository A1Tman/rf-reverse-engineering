# Code Organization

This document explains the code structure for both RF reverse engineering projects.

## Directory Structure

```
rf-reverse-engineering/
├── gazco-fireplace/           # Gazco project directory
│   ├── README.md              # Project documentation
│   ├── buttons.txt            # Raw protocol analysis
│   └── code/                  # Implementation files
│       ├── controller.py      # Unified Gazco controller
│       ├── scripts/           # Individual command scripts
│       │   ├── gazco_on.py    # ON command
│       │   ├── gazco_off.py   # OFF command
│       │   ├── gazco_up.py    # UP command (increase temp)
│       │   └── gazco_down.py  # DOWN command (decrease temp)
│       └── utils/
│           └── convert_gazco.py  # PWM conversion utility
│
├── sonte-smart-film/          # Sonte project directory
│   ├── README.md              # Project documentation
│   └── code/                  # Implementation files
│       ├── sonte_controller.py            # Unified controller class
│       ├── sonte_button1_transparent.py   # Button 1 (transparent)
│       ├── sonte_button2_opaque.py        # Button 2 (opaque)
│       └── sonte_signal_analyzer.py       # PWM analysis utility
│
├── methodology/               # Shared reverse engineering methodology
│   ├── README.md              # Step-by-step RF analysis guide
│   └── screenshots/           # Analysis screenshots (from Sonte session)
│
├── requirements.txt           # Python dependencies
└── README.md                  # Main project documentation
```

## Gazco Fireplace Code

### Two Ways to Use

**Option 1: Unified Controller (Recommended)**
```python
from controller import GazcoController

ctrl = GazcoController()
ctrl.send_command('on')
ctrl.send_command('up')
ctrl.close()
```

**Option 2: Individual Scripts**
```bash
cd gazco-fireplace/code/scripts
python gazco_on.py     # Turn on
python gazco_up.py     # Increase temp
python gazco_down.py   # Decrease temp
python gazco_off.py    # Turn off
```

### Protocol Details
- **Frequency**: 433.876 MHz
- **Modulation**: ASK/OOK
- **PWM Encoding**: 1='100', 0='110'
- **Packet Length**: 23 bits
- **Baud Rate**: ~3100 Hz (controller.py uses 1095 symbol rate)

### Files
- `controller.py` - Modern unified controller with error handling
- `scripts/gazco_*.py` - Original individual command scripts (legacy)
- `utils/convert_gazco.py` - Utility to convert binary to PWM encoding

## Sonte Smart Film Code

### Two Ways to Use

**Option 1: Unified Controller (Recommended)**
```python
from sonte_controller import SonteController

ctrl = SonteController()
ctrl.send_command('button1')    # Make transparent
ctrl.send_command('button2')    # Make opaque
ctrl.close()
```

**Option 2: Individual Scripts**
```bash
cd sonte-smart-film/code
python sonte_button1_transparent.py   # Make transparent
python sonte_button2_opaque.py        # Make opaque
```

### Protocol Details
- **Frequency**: 433.916 MHz
- **Modulation**: ASK/OOK
- **PWM Encoding**: 1='1000', 0='1110'
- **Packet Length**: 15-16 bits (varies by command)
- **Baud Rate**: 2500 Hz

### Files
- `sonte_controller.py` - Unified controller with Norwegian comments
- `sonte_button1_transparent.py` - Button 1 command (Norwegian comments: "Fjernkontrollens key")
- `sonte_button2_opaque.py` - Button 2 command
- `sonte_signal_analyzer.py` - PWM analysis utility (no RF transmission)

## Norwegian Comments in Sonte Code

The Sonte code includes Norwegian language comments from the original February 2019 development session:

- **"Fullstendig PWM key"** = Complete PWM key
- **"Fjernkontrollens key"** = The remote control's key

This reflects the authentic development context and has been preserved in the code.

## Code Evolution

### Gazco (2017-2018)
1. Started with individual script files for each command
2. Later created unified controller class for easier integration
3. Both approaches still available

### Sonte (February 2019)
1. Created individual script files during analysis session
2. Added unified controller for this repository reorganization
3. Preserved Norwegian comments from original development

## Installing and Using

### As Standalone Scripts
```bash
# Install dependencies
pip install -r requirements.txt

# Navigate to project directory
cd gazco-fireplace/code
python scripts/gazco_on.py

cd sonte-smart-film/code
python sonte_button1_transparent.py
```

### Requirements
```bash
pip install -r requirements.txt
```

## Testing

### Gazco
```bash
cd gazco-fireplace/code
python -c "from controller import GazcoController; print('Import successful')"
```

### Sonte
```bash
cd sonte-smart-film/code
python -c "from sonte_controller import SonteController; print('Import successful')"
```

## Notes

- All scripts require RfCat hardware to actually transmit
- Scripts will error if rflib is not installed or RfCat device not connected
- The signal analyzer scripts can run without hardware (just calculate PWM encoding)
- Individual command scripts are "fire and forget" - they execute immediately
- Controller classes provide better error handling and resource management
