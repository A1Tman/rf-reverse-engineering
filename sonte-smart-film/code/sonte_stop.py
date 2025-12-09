#!/usr/bin/env python3
# Send a PWM String using RfCat
# Sonte Smart Film - STOP command

import bitstring
import rflib

prefix = ''
# Fjernkontrollens key (The key from our static key remote)
key = '1111111110111011111100111'

pwm_key = ''.join(['1000' if b == '1' else '1110' for b in key])
full_pwm = '{}{}'.format(prefix, pwm_key)
print('Fullstendig PWM key: {}'.format(full_pwm))

rf_data = bitstring.BitArray(bin=full_pwm).tobytes()
print("Byte string: ",rf_data)
print("PWM Key: ",pwm_key)

d = rflib.RfCat()
d.setMdmModulation(rflib.MOD_ASK_OOK)
d.makePktFLEN(16)
d.setMdmDRate(2500)
d.setMdmSyncMode(0)
d.setFreq(433916000)
d.setMaxPower()

d.RFxmit(b'\x88\x88\x88\x88\x8e\x88\x8e\x88\x88\x88\xee\x88\x80\x00\x00\x00'*4)
d.setModeIDLE()
