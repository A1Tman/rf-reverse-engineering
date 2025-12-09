# Signal Analysis and Reverse Engineering

This document outlines the steps taken to capture, process, and analyze the RF signals used by Gazco fireplaces. It complements the Protocol Specification by demonstrating how raw data was collected and decoded.

---

## 1. Capture Setup

* **Hardware**: Yardstick One USB SDR (Great Scott Gadgets)
* **Antenna**: Quarter-wave 433 MHz whip
* **Software**: RFcat Python library and custom capture script
* **Environment**: Indoor laboratory with minimal RF interference

**Procedure**:

1. Connect Yardstick One and verify with:

   ```bash
   rfcat --version
   ```
2. Capture raw samples:

   ```python
   from rflib import RfCat
   d = RfCat()
   d.setFreq(433_876_000)        # 433.876 MHz
   d.savingSamples('signals.raw')
   d.RFxmitOpen()                # Enable RX
   input('Press Enter to stop capture...')
   d.RFxmitClose()
   ```
3. Import `signals.raw` into URH or Audacity for waveform viewing.

---

## 2. Raw Waveform Inspection

**Audacity Export**:

* Import `signals.raw` as 32-bit float at 320 kHz sample rate (mono).
* Zoom into a single button press (\~7 ms duration).

**Key Observations**:

* High/low ASK pulses are clearly defined.
* Pulse durations cluster around \~300 and \~600 samples.
* A distinctive preamble appears at each frame’s start.

![Zoomed PWM waveform](../analysis/figure002.png)

---

## 3. Symbol Timing Extraction

**Data Analysis**:

1. Parse sample runs (high/low) in `signals.raw`.
2. Measure shortest and longest runs: \~292 and \~601 samples.
3. Compute symbol rate:

   ```python
   short, long = 292, 601
   baud = 1.0 / (short / 320000)
   print(f"Measured symbol rate: {baud:.0f} symbols/s")  # ~1095 symbols/s
   ```

---

## 4. PWM Decoding

Translate sample-run lengths into bits:

* **Run ≤ 350 samples** → binary `1`
* **Run > 350 samples** → binary `0`

**Resulting 23-bit frame**:

```
10000011101110010000100
```

---

## 5. Byte Conversion

Use the converter utility to map PWM to bytes:

```bash
python -m gazco_rf.utils.convert_gazco > pwm_bytes.txt
```

**Sample output**:

```
PWM Key: 100110110110110110100100100110100100100110110100110110110110100110110
Byte string: b"\x9bm\xa4\x9aI\xb4\xdbi\xb0"
```

---

## 6. Validation

1. Transmit the byte string via RFcat:

   ```python
   from gazco_rf.controller import GazcoController
   ctrl = GazcoController()
   ctrl.send_command('on')
   ```
2. Verify the fireplace responds to `on`, `off`, `up`, and `down` commands.
3. Repeat tests to confirm reliability.

---

*End of signal analysis.*
