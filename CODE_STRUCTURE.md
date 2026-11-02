# Code organization

The two controllers share one hardware-lazy sender. Imports, controller
construction, help, and dry runs do not open a dongle.

```text
rf-reverse-engineering/
├── rf_signals.py                    # Shared Transmission and checked send path
├── TRANSMISSIONS.md                 # Recorded-byte provenance and uncertainties
├── gazco-fireplace/
│   ├── buttons.txt                 # Historical decoded notes
│   └── code/
│       ├── controller.py           # GazcoController and CLI
│       ├── gazco_profiles.py       # Immutable complete bursts
│       ├── scripts/gazco_*.py      # Wrappers for on/off/up/down
│       └── utils/convert_gazco.py   # Optional bitstring-based encoding example
├── sonte-smart-film/
│   └── code/
│       ├── sonte_controller.py     # SonteController and CLI
│       ├── sonte_profiles.py       # Immutable button1/button2/original bursts
│       ├── sonte_button1_transparent.py
│       ├── sonte_button2_opaque.py
│       └── sonte_signal_analyzer.py
├── tests/
│   ├── fixtures/transmissions.json # Independent pre-reconciliation references
│   └── test_transmissions.py       # Offline behavior and byte checks
├── tools/check_documentation.py    # Local links and marked offline CLI examples
└── .github/workflows/offline-checks.yml
```

## Inspect from the repository root

No dependency installation is needed for these commands:

<!-- offline-smoke -->
```bash
python gazco-fireplace/code/controller.py on --dry-run
python gazco-fireplace/code/scripts/gazco_up.py --dry-run
python sonte-smart-film/code/sonte_controller.py original --dry-run
python sonte-smart-film/code/sonte_button1_transparent.py --dry-run
```

The optional conversion utilities use `bitstring` 4.x from `requirements.txt`.
They calculate encodings,
not complete transmit bursts. See [the public quick start](README.md#quick-start)
and [the analysis guide](analysis/protocol_docs/signal_analysis.md).

## Programmatic use

From `gazco-fireplace/code`, after setting up
[radio access](README.md#radio-access-for-maintainers):

```python
from controller import GazcoController

controller = GazcoController()  # No hardware opened yet.
if not controller.send_command('on'):
    raise RuntimeError('Gazco transmission could not be submitted')
```

For Sonte, import `SonteController` from `sonte_controller` while in
`sonte-smart-film/code`. Its profiles are `button1`, `button2`, and `original`.
The first two retain historical transparent/opaque labels; `original` has no
assigned physical meaning.

A valid actual send opens RfCat lazily, applies the recorded settings, submits
the complete bytes once, checks the return status, and attempts IDLE cleanup.
Programmatic failure returns `False`; CLI failure returns a nonzero exit status.
The sender does not add host repeat loops or delays. Submission does not prove
target reception. See [TRANSMISSIONS.md](TRANSMISSIONS.md) for the legacy
`None` status compatibility limit and exact bytes.

## Protocol quantities

| Device | Carrier setting | Data-rate setting | Logical key | FLEN byte setting |
|---|---:|---:|---|---|
| Gazco | 433876000 Hz | 1095 symbols/s | 23 bits; PWM `1=100, 0=110` | 23 |
| Sonte | 433916000 Hz | 2500 symbols/s | 24–25 bits; PWM `1=1000, 0=1110` | 15 or 16 |

The logical key length, FLEN argument, and complete burst length are separate.
The historical Gazco timing calculation is `320000 / 292`, approximately 1095.89
units/s; the scripts preserve the 1095 setting.

## History and language

Gazco work began with individual scripts in 2017–2018 and later gained a unified
controller. The Sonte analysis dates to February 2019; its analyzer retains
Norwegian comments such as “Fjernkontrollens key” (the remote control's key).
The shared profiles now keep controller and wrapper transmissions identical.
They preserve the earlier recorded bursts rather than infer new values.

## Checks

Run from the repository root:

```bash
python -m unittest discover -s tests -v
python tools/check_documentation.py
```

After installing the optional requirements, `python tools/check_converters.py`
checks both conversion utilities against frozen output bytes without loading
radio modules. The core checks above require no dependency installation.

The tests use fake radios and independent saved fixtures. They do not establish
new hardware or physical-device results.
