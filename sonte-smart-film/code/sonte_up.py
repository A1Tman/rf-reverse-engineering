#!/usr/bin/env python3
# Send a PWM String using RfCat
# Sonte Smart Film - UP command (make transparent)

import bitstring
import rflib

# That prefix string. This was determined by literally
# just looking at the waveform, and calculating it relative
# to the clock signal value.
# Your remote may not need this.
prefix = ''

# Fjernkontrollens key (The key from our static key remote)
key = '1111111110111011111100111'

# Convert the data to a PWM key by looping over the
# data string and replacing a 1 with 1000 and a 0
# with 1110
pwm_key = ''.join(['1000' if b == '1' else '1110' for b in key])

# Join the prefix and the data for the full pwm key
full_pwm = '{}{}'.format(prefix, pwm_key)
print('Fullstendig PWM key: {}'.format(full_pwm))

# Convert the data to hex
rf_data = bitstring.BitArray(bin=full_pwm).tobytes()
print(bitstring.BitArray(bin=full_pwm).tobytes())
print("Byte string: ",rf_data)
print("PWM Key: ",pwm_key)

# Start up RfCat
d = rflib.RfCat()

# Set Modulation. We using On-Off Keying here
d.setMdmModulation(rflib.MOD_ASK_OOK)

# Configure the radio
d.makePktFLEN(15)        # Set the RFData packet length
d.setMdmDRate(2500)      # Set the Baud Rate
d.setMdmSyncMode(0)      # Disable preamble
d.setFreq(433916000)     # Set the frequency
d.setMaxPower()

# Send the data string a few times
d.RFxmit(b'\x88\x88\x88\x88\xe8\x88\xe8\x88\x88\x88\x8e\x88\x00\x00\x00\x88\x88\x88\x88\x8e\x88\x8e\x88\x88\x88\x88\xe8\x80\x00\x00\x00\x88\x88\x88\x88\x8e\x88\x8e\x88\x88\x88\x88\xe8\x80\x00\x00\x00\x88\x88\x88\x88\x8e\x88\x8e\x88\x88\x88\x88\xe8\x80\x00\x00\x00\x88\x88\x88\x88\x8e\x88\x8e\x88\x88\x88\x88\xe8\x80\x00\x00\x00')
d.setModeIDLE()
