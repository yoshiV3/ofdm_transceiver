#Modulation
PAYLOAD_BPS = 2
HEADER_BPS  = 1

#SCRAMBLING
SCRAMBLED_SEED   = 0x7F 
PILOT_SEED       = 42
SYNC_SEED        = 41
PILOT_SEQ_LENGTH = 64


#PLuto SDR
CENTRAL_FREQUENCY = 1000000000 #1.8 Ghz
BANDWIDTH_RF      = 2000000    #10 MHz
SAMPLE_RATE       = 2000000
BUFFER_SIZE       = 0x8000
MANUAL_GAIN       = 30.0
GAIN_MODE         = "manual"
AUTO_FILTER       = False
DC_TRACKING       = False
BB_TRACKING       = TRUE
QUADRA_TRACKING   = False
ATTENUATION       = 20
RECEIVER          = "192.168.3.2"
TRANSMITTER       = "192.168.2.1"
FILTER            = ''

#ofdm 
TONES_POSITIVE = list(range(1,7)) + list(range(8,21)) + list(range(22,27))
TONES_NEGATIVE = list(range(-26,-21)) + list(range(-20,-7)) + list(range(-6,0))
PILOT_TONES    = [-7,-21, 7, 21]
FFT_LENGTH     = 64
CP_LENGTH      = 16

#tag keys 
LENGTH_TAG_KEY    = "packet_len"
LENGTH_HEADER_KEY = "header_len" 
LENGTH_PACKET_KEY = "packet_len"
