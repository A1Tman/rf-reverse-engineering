#!/usr/bin/python

# Sonte Smart Film - Signal Analyzer
# Converts binary key to PWM encoding for analysis

# Fjernkontrollens key (The key from our static key remote)
import bitstring

key = '1111111110111011111100111'

# Convert the data to a PWM key by looping over the
# data string and replacing a 1 with 1000 and a 0
# with 1110
pwm_key = ''.join(['1000' if b == '1' else '1110' for b in key])
rf_data=bitstring.BitArray(bin=pwm_key).tobytes()
print("Byte string: ",rf_data)
print("PWM Key: ",pwm_key)
