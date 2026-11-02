# Recorded transmissions and provenance

Controllers and standalone scripts now use the same immutable device profiles
and send each complete recorded burst in one `RFxmit(payload)` call. Repetition
and zero padding are part of those bytes. The shared sender does not replace
them with delays between host-side calls or add an RFcat repeat argument.

The prior Gazco controller sent unpadded nine-byte fragments separately with
50 ms sleeps. Its `on`, `off`, `up`, and `down` commands now send exactly the
pre-existing standalone-script bursts. This is an intentional controller
behavior change to make both entry points agree; the standalone waveforms are
unchanged. These profiles are regression references, not new hardware validation.

## Gazco references

The default profiles reproduce scripts at commit `43ef809`. Those scripts and
the previous controller first entered this repository together in `45b3760`
on 9 December 2025. Earlier evidence is the note in
[`RF_Projects/docs/Gazco button up.txt`](https://github.com/A1Tman/RF_Projects/blob/0a1d1e3/docs/Gazco%20button%20up.txt),
committed on 31 August 2024. That earlier repository contains the Gazco note,
but no Gazco transmitter scripts in its original history.

| Command | Bytes per frame | Frames in one burst | Burst bytes |
|---|---:|---:|---:|
| `on` | 16 | 9 | 144 |
| `off` | 15 | 10 | 150 |
| `up` | 16 | 10 | 160 |
| `down` | 16 | 10 | 160 |
| `down_notes_19` (explicit alternative) | 16 | 19 | 304 |

All keep 433876000 Hz, 1095 baud, ASK/OOK, sync mode zero, the existing power
setting and `makePktFLEN(23)` call. FLEN is an RFcat byte-setting argument;
the decoded command's 23 logical bits are a separate quantity. These settings
were preserved, not inferred from the payload length.

The notes explain important choices:

- Lines 16–18 derive 1095 baud from a 292-sample pulse at 320 kHz.
- Line 25 labels the OFF zero padding as the pause between signals.
- Lines 40–47 record nineteen DOWN repetitions and explicitly include the
  additional `b0` byte and six zero bytes as padding.

Two disagreements remain explicit:

- **DOWN:** the existing standalone script repeats ten frames; the earlier
  note says nineteen. `down` retains ten. `down_notes_19` provides the documented
  nineteen-frame alternative without overwriting the default. Its 304-byte
  burst uses RFcat's long-transmission path with no repeat argument.
- **ON:** the earlier note lists six trailing zero bytes and a dangling
  backslash, while the script contains seven. `on` keeps the script's seven;
  the discrepancy needs capture or hardware evidence, not a guessed correction.

## Sonte references

`button1` and `button2` retain their exact 79-byte bursts and existing labels,
with FLEN 15 and 16 respectively. Both keep 433916000 Hz and 2500 baud.
Their labels are not a new verification of the physical button mapping.

The `original` command restores the transmission from
[`RF_Projects/scripts/sonteremote.py`](https://github.com/A1Tman/RF_Projects/blob/599a308/scripts/sonteremote.py),
added on 31 August 2024:

```python
bytes.fromhex("888888888e888e888888ee8880000000") * 4
```

It sends 64 bytes in one call and retains FLEN 16, 2500 baud and 433916000 Hz.
The newer repository had copied these bytes under the incorrect `stop` label,
then deleted them in `210db8f` on 9 December 2025. `original` deliberately
assigns no transparent/opaque/STOP meaning. It does not replace either button.

## Inspect and test without hardware

Run from the repository root:

```bash
python gazco-fireplace/code/controller.py on --dry-run
python gazco-fireplace/code/controller.py down_notes_19 --dry-run
python sonte-smart-film/code/sonte_controller.py original --dry-run
python gazco-fireplace/code/scripts/gazco_on.py --dry-run
python -m unittest discover -s tests -v
```

Imports, controller construction, `--help`, invalid command validation, and
`--dry-run` do not import RfCat or open hardware. Actual send operations import
RfCat lazily, check its return status, and attempt IDLE cleanup on success,
configuration failure, transmission failure, or interruption. Programmatic
`send_command` returns a boolean; CLI failure returns a nonzero exit status.
Profiles are immutable; recorded bytes are available through
`controller.profiles[command].data`.

Use the maintained [Python 3 RfCat fork](https://github.com/A1Tman/rfcat_py3)
for numeric firmware-status reporting. Older RfCat versions return `None` for
short sends; compatibility with that API cannot detect failures the old library
discarded. A successful submission never proves reception by the target.

`tests/fixtures/transmissions.json` freezes bytes, settings, source pointers
and hashes captured before reconciliation. Tests assert these independent
references against the controllers and standalone wrappers, including the
304-byte alternative, error statuses, cleanup, and hardware-free operation.
No radio or physical device was used for these tests. Historical documentation
claims of hardware validation are not independently established by this work.
