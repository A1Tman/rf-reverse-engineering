# Gazco recorded protocol and transmission reference

This reference separates the decoded command patterns from the exact bursts
preserved by the current controllers. The original Gazco work dates to
2017–2018. Current software checks compare recorded bytes and settings; they
do not establish new on-air timing or physical fireplace behavior.

The authoritative implementation is
[`gazco_profiles.py`](../../gazco-fireplace/code/gazco_profiles.py). See
[TRANSMISSIONS.md](../../TRANSMISSIONS.md) for source commits, historical notes,
and unresolved differences. Do not reconstruct a transmit burst from the
logical command table alone.

## Units and settings

| Quantity | Preserved value or interpretation |
|---|---|
| Carrier setting | 433876000 Hz |
| Modulation | ASK/OOK |
| Data-rate setting | 1095 symbols/s |
| Decoded command | 23 logical bits |
| PWM mapping | `1 → 100`, `0 → 110` |
| Encoded command | 69 PWM bits, occupying nine bytes after byte alignment |
| RFcat fixed-length setting | `makePktFLEN(23)` — a byte-setting argument, not 23 logical bits |
| Sync mode | Zero, as in the original scripts |
| Transmit input | One complete recorded burst, including extra bytes, zero padding, and repetitions |

FLEN is a preserved hardware setting and is not the total burst length. Its
interaction with the installed firmware must be checked on hardware; changing
it to match a derived length would change the historical configuration.

## Command patterns and field hypotheses

The four recorded patterns share the first 17 bits:

| Command | Full logical pattern | Last six bits |
|---|---|---|
| `on` | `10000011101110010001100` | `001100` |
| `off` | `10000011101110010001000` | `001000` |
| `up` | `10000011101110010000100` | `000100` |
| `down` | `10000011101110010000010` | `000010` |

The original analysis proposed a seven-bit preamble, ten-bit address, and
six-bit command. Those field meanings were not confirmed; the shared prefix
and varying suffix are observations from these patterns, not a verified
manufacturer protocol layout. No checksum or address semantics are inferred
by the controller.

## Timing rationale

The historical notes measured a shortest pulse of 292 samples at a sample
rate of 320000 samples/s:

```python
sample_rate = 320000
shortest_pulse_samples = 292
baud = sample_rate / shortest_pulse_samples  # approximately 1095.89
```

The preserved scripts use 1095. One encoded high/low unit at that setting is
approximately `1 / 1095` seconds, or 0.913 ms. A logical bit occupies three
units, approximately 2.74 ms before gaps. Three PWM units are not three samples
of the captured waveform. The analysis sample rate and the transmit symbol
rate are different quantities.

Inter-frame timing is represented by bytes in the saved bursts. The sender
does not insert 50 ms Python sleeps. These calculations explain the setting;
they do not replace a measurement of the installed firmware's RF output.

## Complete recorded bursts

Each row describes the frame bytes preserved in the scripts and how many
copies appear in the burst. `00 × N` denotes explicit zero bytes.

| Profile | Recorded frame bytes | Frame bytes | Frames | Burst bytes |
|---|---|---:|---:|---:|
| `on` | `9b 6d a4 9a 49 b4 db 49 b0`, then `00 × 7` | 16 | 9 | 144 |
| `off` | `9b 6d a4 9a 49 b4 db 4d b0`, then `00 × 6` | 15 | 10 | 150 |
| `up` | `9b 6d a4 9a 49 b4 db 69 b0 b0`, then `00 × 6` | 16 | 10 | 160 |
| `down` | `9b 6d a4 9a 49 b4 db 6d 30 b0`, then `00 × 6` | 16 | 10 | 160 |
| `down_notes_19` | Same frame as `down` | 16 | 19 | 304 |

The additional `b0` in UP/DOWN and the zero padding belong to the recorded
frames. The sender passes those bytes unchanged; it does not infer padding
from FIFO size. Eight-byte excerpts omit meaningful trailing data.

Two historical disagreements remain deliberate: ON retains the script's seven
zero bytes although an earlier note lists six; DOWN defaults to the script's
ten frames, with nineteen exposed only as `down_notes_19`. The complete
304-byte alternative uses the long-transmission path without a host repeat
argument. Capture or hardware evidence is needed before changing either choice.

## Inspect and validate without a radio

Run from the repository root:

<!-- offline-smoke -->
```bash
python gazco-fireplace/code/controller.py on --dry-run
python gazco-fireplace/code/controller.py down_notes_19 --dry-run
```

The output includes the exact settings, full payload hex, and burst length.
`python -m unittest discover -s tests -v` compares all profiles against frozen
pre-reconciliation fixtures. To submit a real command after configuring the
[radio dependency](../../README.md#radio-access-for-maintainers), omit
`--dry-run` from a controller command. A successful submission is not an
acknowledgement from the fireplace.
