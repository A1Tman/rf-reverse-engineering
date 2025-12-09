# Convert a static binary key to PWM and bytes
# Key from static Gazco remote (23-bit command)
import bitstring

key = '10000011101110010000010'

# Convert each bit: '1' -> '100', '0' -> '110'
pwm_key = ''.join('100' if bit == '1' else '110' for bit in key)

# Convert PWM bitstring to bytes
erf_data = bitstring.BitArray(bin=pwm_key).tobytes()

print("PWM Key:", pwm_key)
print("Byte string:", erf_data)