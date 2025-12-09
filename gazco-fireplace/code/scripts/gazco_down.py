#!/usr/bin/env python3
# Send a PWM String using RfCat  
# Gazco Fireplace - DOWN command

import rflib

# Start up RfCat
d = rflib.RfCat()

# Set Modulation. We using On-Off Keying here
d.setMdmModulation(rflib.MOD_ASK_OOK)

# Configure the radio
d.makePktFLEN(23)        # Set the RFData packet length
d.setMdmDRate(1095)      # Set the Baud Rate
d.setMdmSyncMode(0)      # Disable preamble
d.setFreq(433876000)     # Set the frequency
d.setMaxPower()

# Send the data string a few times
d.RFxmit(b'\x9bm\xa4\x9aI\xb4\xdbm0\xb0\x00\x00\x00\x00\x00\x00'*10)
d.setModeIDLE()
