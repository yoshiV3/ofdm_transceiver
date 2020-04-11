#Modulation
PAYLOAD_BPS = 2 #bit per symbol for the payload 
HEADER_BPS  = 1 #bits per symbol for the header: lower than the bits per symbol in the payload, because more critical to receive correctly

#SCRAMBLING
SCRAMBLED_SEED   = 0x7F  #seed for the scrambling of the bits
PILOT_SEED       = 42    #seed to generate the pilot symbols
SYNC_SEED        = 41    #seed to generate the sync words
PILOT_SEQ_LENGTH = 64    #how many symbols (data and header) before reuse of the pilot symmbols


#PLuto SDR
CENTRAL_FREQUENCY = 1800000000 #1.8 Ghz central frequency
BANDWIDTH_RF      = 2000000    #10 MHz RF bandwidth
SAMPLE_RATE       = 2000000   #sample rate 
BUFFER_SIZE       = 0x8000 
MANUAL_GAIN       = 30.0
GAIN_MODE         = "manual"
AUTO_FILTER       = False
DC_TRACKING       = False      #DC offset tracking
BB_TRACKING       = True       #Baseband tracking
QUADRA_TRACKING   = False      # quadrature tracking
ATTENUATION       = 20
RECEIVER          = "192.168.3.2" #IP address of the receiver and the transmitter side
TRANSMITTER       = "192.168.2.1"
FILTER            = ''     # no special filter 

#ofdm 
TONES_POSITIVE = list(range(1,7)) + list(range(8,21)) + list(range(22,27))   #positive tones  used for data 
TONES_NEGATIVE = list(range(-26,-21)) + list(range(-20,-7)) + list(range(-6,0))  #negative tones for data 
PILOT_TONES    = [-7,-21, 7, 21]  #pilot tones
FFT_LENGTH     = 64               #length of the FFT
CP_LENGTH      = 16               #cyclic prefix 

#tag keys 
LENGTH_TAG_KEY    = "packet_len" #tags for metadata on the stream 
LENGTH_HEADER_KEY = "header_len" 
LENGTH_PACKET_KEY = "packet_len"
