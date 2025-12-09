# RF Reverse Engineering Methodology

**A systematic approach to analyzing and decoding unknown RF protocols using Software Defined Radio techniques.**

## Overview

This document describes the methodology used to reverse engineer two independent 433 MHz remote control protocols (Gazco fireplace and Sonte smart film). The process is generalizable to other RF protocols in the ISM bands.

**Note on Documentation**: The workflow screenshots in this directory are from the Sonte smart film analysis session (February 2019), as that project included systematic documentation. However, the methodology, tools, and process were identical for both projects - only the frequency and protocol details differ.

## Prerequisites

### Hardware
- **SDR Receiver**: RTL-SDR, HackRF, or similar (for signal analysis)
- **RfCat Device**: YARD Stick One or cc1111-based USB dongle (for transmission)
- **Target Device**: The remote control to be analyzed

### Software
- **SDR#** or **HDSDR**: For initial frequency discovery and signal visualization
- **GNU Radio**: For signal processing and demodulation
- **Audacity**: For visual timing analysis of demodulated signals
- **Python 3.6+**: With numpy, matplotlib for custom analysis
- **RfCat**: For transmission and testing

## Step-by-Step Process

### Phase 1: Frequency Discovery

**Objective**: Identify the transmission frequency of the unknown remote control.

**Tools**: SDR# or HDSDR with RTL-SDR

**Process**:
1. Connect SDR receiver with appropriate antenna for 433 MHz
2. Open SDR software and navigate to 433 MHz ISM band (433.05 - 434.79 MHz)
3. Set appropriate bandwidth (typically 2-3 MHz span)
4. Press buttons on target remote while observing waterfall display
5. Note the precise frequency of signal bursts

**Expected Results**:
- Clear signal spikes in waterfall display
- Consistent frequency across multiple button presses
- Signal strength significantly above noise floor

![Frequency Discovery](screenshots/01_frequency_discovery_sdr_sharp.png)
*Figure 1: Initial frequency discovery showing 433.916 MHz signal in SDR# waterfall display*

**Key Observations**:
- Signals appear as vertical lines in waterfall
- Multiple repeated transmissions per button press
- Frequency stability indicates crystal-controlled transmitter

---

### Phase 2: Raw Signal Capture

**Objective**: Capture clean RF signal samples for detailed analysis.

**Tools**: HDSDR, GNU Radio

**Process**:
1. Tune to exact frequency identified in Phase 1
2. Configure demodulation mode (typically AM for ASK/OOK signals)
3. Set appropriate sample rate (typically 320 kHz or higher)
4. Record signal while pressing target button multiple times
5. Save IQ samples or demodulated audio

**Expected Results**:
- Clean on-off keying (OOK) patterns visible
- Consistent packet timing
- Minimal noise between transmissions

![Raw Signal Capture](screenshots/02_raw_signal_capture_hdsdr.png)
*Figure 2: Raw RF signal capture showing ASK/OOK modulation envelope*

**Technical Notes**:
- Higher sample rates provide better timing resolution
- Multiple captures help identify consistent patterns
- Record at least 5-10 button presses for validation

---

### Phase 3: Signal Demodulation & PWM Analysis

**Objective**: Extract digital data from modulated RF carrier.

**Tools**: Audacity, GNU Radio, Python

**Process**:
1. Import captured signal into Audacity
2. Zoom into individual pulses to measure timing
3. Identify pulse width patterns (PWM encoding)
4. Count samples for different pulse widths
5. Determine the mapping between pulse widths and binary data

**Expected Results**:
- Two distinct pulse widths representing '0' and '1'
- Consistent timing across multiple captures
- Clear start/stop patterns

![PWM Pattern Analysis](screenshots/03_pwm_pattern_analysis_audacity.png)
*Figure 3: Detailed PWM pattern analysis revealing encoding scheme*

**Common PWM Encoding Schemes**:
```
Manchester Encoding:
  1 = '10'
  0 = '01'

Short/Long Pulse (Common in 433 MHz):
  1 = short pulse (e.g., 300 samples)
  0 = long pulse (e.g., 600 samples)

Project-Specific Examples:
  Gazco:  1='100', 0='110'
  Sonte:  1='1000', 0='1110'
```

**Timing Measurements**:
```python
# Calculate baud rate from sample timing
sample_rate = 320000  # Hz
shortest_pulse = 292  # samples
baud_rate = sample_rate / shortest_pulse
# Result: ~1095 Hz per symbol
```

---

### Phase 4: Protocol Extraction

**Objective**: Convert PWM timing into binary data and identify command structure.

**Tools**: Python with numpy, custom analysis scripts

**Process**:
1. Write Python script to parse demodulated signal
2. Threshold signal to binary (on/off)
3. Measure pulse widths and convert to binary
4. Extract bit patterns for each button
5. Identify packet structure and repeated patterns

**Expected Results**:
- Binary command patterns for each button
- Packet length identification
- Command structure understanding

![Signal Processing](screenshots/04_signal_processing_matplotlib.png)
*Figure 4: Python-based signal processing showing binary extraction*

**Example Analysis Output**:
```
Gazco UP Button:
  Binary: 10000011101110010000100
  Length: 23 bits
  Repeats: 10 times
  PWM:    100110110110110110100100100110100100100110110100110110110110100110110

Command Structure Analysis:
  Preamble: 1000001 (7 bits)
  ID/Address: 1101110010 (10 bits)
  Command: 000100 (6 bits)
```

---

### Phase 5: Frequency Domain Validation

**Objective**: Verify signal characteristics and confirm modulation scheme.

**Tools**: GNU Radio, FFT analysis

**Process**:
1. Perform FFT on captured signal
2. Verify center frequency matches discovery
3. Measure signal bandwidth
4. Confirm modulation type (ASK/OOK)

**Expected Results**:
- Clean spectral peak at carrier frequency
- Bandwidth consistent with baud rate
- No unexpected harmonics or spurious emissions

![Frequency Domain Analysis](screenshots/05_frequency_domain_analysis_gnuradio.png)
*Figure 5: FFT analysis confirming spectral characteristics*

**Analysis Checklist**:
- [ ] Center frequency matches initial discovery
- [ ] Bandwidth = 2 × baud rate (approximately)
- [ ] No significant sidebands beyond expected range
- [ ] Signal-to-noise ratio > 20 dB

---

### Phase 6: Implementation & Testing

**Objective**: Implement working transmitter to validate protocol understanding.

**Tools**: RfCat, Python

**Process**:
1. Configure RfCat radio parameters:
   - Frequency
   - Modulation (ASK/OOK)
   - Baud rate
   - Packet length

2. Implement PWM encoding function

3. Transmit test commands

4. Verify device response

**Example Implementation**:
```python
import rflib

class RFController:
    def __init__(self, frequency):
        self.d = rflib.RfCat()
        self.d.setFreq(frequency)
        self.d.setMdmModulation(rflib.MOD_ASK_OOK)
        self.d.setMdmDRate(3100)  # Baud rate in Hz
        self.d.makePktFLEN(23)     # Packet length in bits

    def pwm_encode(self, binary_string):
        """Convert binary to PWM bytestring"""
        pwm = ''
        for bit in binary_string:
            if bit == '1':
                pwm += '100'   # Short pulse
            else:
                pwm += '110'   # Long pulse
        return self.pwm_to_bytes(pwm)

    def send_command(self, binary_cmd, repeats=10):
        """Send command with repetitions"""
        data = self.pwm_encode(binary_cmd)
        for _ in range(repeats):
            self.d.RFxmit(data)
            time.sleep(0.01)
```

**Validation Process**:
1. Test each button command individually
2. Verify device responds correctly
3. Test at various distances
4. Confirm no interference with other devices

---

## Common Challenges & Solutions

### Challenge 1: Noisy Signal
**Solution**:
- Use better antenna
- Move closer to target
- Increase SDR gain carefully (watch for overload)
- Apply filtering in GNU Radio

### Challenge 2: Inconsistent Timing
**Solution**:
- Higher sample rate for better resolution
- Average multiple captures
- Account for clock drift in analysis

### Challenge 3: Complex Encoding
**Solution**:
- Capture many different commands
- Look for patterns in binary representation
- Consider checksums, rolling codes, or encryption

### Challenge 4: Device Not Responding
**Solution**:
- Verify all radio parameters (frequency, modulation, baud rate)
- Check PWM encoding accuracy
- Ensure adequate transmission power
- Verify packet repetition matches original

---

## Best Practices

### Documentation
- Screenshot each analysis step
- Record all measurements and observations
- Note exact tool versions and settings
- Keep raw capture files for future reference

### Analysis
- Always capture multiple examples of each command
- Compare captures to identify consistent patterns
- Start with simple commands before complex ones
- Validate understanding at each phase

### Safety & Legal
- Only analyze and control devices you own
- Respect local RF regulations (power, duty cycle)
- Ensure no interference with critical systems
- Follow responsible disclosure for security issues

### Code Quality
- Write clean, well-commented code
- Include parameter validation
- Handle errors gracefully
- Provide usage examples

---

## Tools Reference

| Tool | Purpose | Download |
|------|---------|----------|
| **SDR#** | Frequency discovery, waterfall | [airspy.com](https://airspy.com/download/) |
| **HDSDR** | Signal capture, recording | [hdsdr.de](http://www.hdsdr.de/) |
| **GNU Radio** | Signal processing, demodulation | [gnuradio.org](https://www.gnuradio.org/) |
| **Audacity** | Audio timing analysis | [audacityteam.org](https://www.audacityteam.org/) |
| **RfCat** | RF transmission, testing | [github.com/atlas0fd00m/rfcat](https://github.com/atlas0fd00m/rfcat) |
| **Universal Radio Hacker** | All-in-one RF analysis | [github.com/jopohl/urh](https://github.com/jopohl/urh) |

---

## Learning Resources

- **RTL-SDR Blog**: Tutorials and guides for SDR beginners
- **GNU Radio Tutorials**: Signal processing fundamentals
- **RfCat Documentation**: Hardware control and transmission
- **ISM Band Regulations**: FCC Part 15 (US) or equivalent local regulations

---

## Project Timeline Comparison

| Phase | Gazco Project | Sonte Project |
|-------|---------------|---------------|
| **Discovery** | 2017-2018 | February 2019 |
| **Analysis** | Undocumented | Feb 3, 2019 (screenshots) |
| **Implementation** | 2018 | February 2019 |
| **Documentation** | Retrospective | Concurrent |

The Sonte project benefited from lessons learned during the Gazco analysis, resulting in better documentation practices and more systematic screenshot capture.

---

## Conclusion

This methodology provides a reproducible framework for RF protocol reverse engineering. While specific parameters vary between devices (frequency, encoding, packet structure), the fundamental process remains consistent:

1. **Discover** the frequency
2. **Capture** clean signals
3. **Demodulate** to extract timing
4. **Decode** the protocol structure
5. **Validate** through spectral analysis
6. **Implement** and test

By following these steps systematically and documenting thoroughly, unknown RF protocols can be reliably analyzed and reimplemented for research, education, and authorized control applications.
