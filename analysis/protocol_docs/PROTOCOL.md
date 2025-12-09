# Gazco RF Protocol Technical Documentation

This document describes the reverse-engineered RF protocol for controlling Gazco fireplaces via a 433.876 MHz ASK/OOK link, including timing, frame structure, PWM encoding, and command formats.

---

## 1. Overview

- **Carrier Frequency**: 433.876 MHz (± tolerance)  
- **Modulation**: ASK/OOK (Amplitude Shift Keying / On-Off Keying)  
- **Symbol Rate**: ~1095 symbols/s  
- **Packet Length**: 23 bits  
- **Inter-Packet Gap**: ~50 ms  

---

## 2. Frame Structure

Each button press transmits a 23‑bit command frame, repeated to ensure reliability.

```
[23‑bit Command] → pause → repeat
```

- **Repetition Counts**:
  - `on`: 9 repeats  
  - `off`: 10 repeats  
  - `up`: 10 repeats  
  - `down`: 19 repeats  

---

## 3. Bitfields

### 3.1 Fixed Header (Bits 22–3)

```
10000011101110010000
```

This 20‑bit preamble/sync pattern is constant across all commands.

### 3.2 Command Bits (Bits 2–0)

| Command | Bits [2:0] | Full 23‑bit Pattern              |
|---------|------------|----------------------------------|
| **on**  | `100`      | `10000011101110010000`**`100`**  |
| **off** | `000`      | `10000011101110010000`**`000`**  |
| **up**  | `001`      | `10000011101110010000`**`001`**  |
| **down**| `010`      | `10000011101110010000`**`010`**  |

> **Note:** The original remote uses `up` and `on` with identical header+command bits but differentiates by repeat count.

---

## 4. PWM Encoding

Before RF transmission, each binary bit is mapped to a 3‑symbol PWM sequence:

```python
# Pseudocode conversion
def pwm_sequence(bit):
    return '100' if bit == '1' else '110'
```

- **`1` → `100`**: short ON, long OFF  
- **`0` → `110`**: long ON, short OFF  

Symbol timing at 320 kHz sample rate: each PWM symbol (3 samples) ≈ 9.4 µs.

---

## 5. Hex Payloads

The controller sends raw bytes corresponding to the 23‑bit frame (padded to 8 bytes):

| Command | Payload Bytes (hex)       | Length |
|---------|---------------------------|--------|
| **on**  | `9B 6D A4 9A 49 B4 DB 49` | 8 bytes |
| **off** | `9B 6D A4 9A 49 B4 DB 4D` | 8 bytes |
| **up**  | `9B 6D A4 9A 49 B4 DB 69` | 8 bytes |
| **down**| `9B 6D A4 9A 49 B4 DB 6D` | 8 bytes |

> **Padding**: Remaining zero bytes (if any) are appended by the controller library to match hardware FIFO lengths.

---

## 6. Timing and Reliability

- **Inter-Packet Gap**: Each frame repeat is separated by ~50 ms to allow the receiver to resynchronize.  
- **No Checksum**: Reliability is achieved via fixed header, repeat counts, and gap timing.

---

## 7. RfCat Configuration Example

```python
from rflib import RfCat, MOD_ASK_OOK

d = RfCat()
d.setMdmModulation(MOD_ASK_OOK)  # ASK/OOK
d.makePktFLEN(23)                 # 23 bit payload
d.setMdmDRate(1095)               # symbol rate
d.setMdmSyncMode(0)               # no preamble
d.setFreq(433_876_000)            # 433.876 MHz
d.setMaxPower()
```

---

*This document reflects empirical reverse‑engineering and has been validated with multiple captures and transmissions.*
