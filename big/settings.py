#Modulation
PAYLOAD_BPS = 2 #bit per symbol for the payload 
HEADER_BPS  = 1 #bits per symbol for the header: lower than the bits per symbol in the payload, because more critical to receive correctly

#SCRAMBLING
SCRAMBLED_SEED   = 0x7F  #seed for the scrambling of the bits
PILOT_SEED       = 42    #seed to generate the pilot symbols
SYNC_SEED        = 41    #seed to generate the sync words
PILOT_SEQ_LENGTH = 64    #how many symbols (data and header) before reuse of the pilot symmbols

thousand =  1000
million  =  thousand**2
#PLuto SDR
CENTRAL_FREQUENCY = 1700000000 #1.8 Ghz central frequency
BANDWIDTH_RF      = int(million)#20000000    #10 MHz RF bandwidth
SAMPLE_RATE       = int(million)   #sample rate 
BUFFER_SIZE       = 0xFFFF
MANUAL_GAIN       = 64.0
GAIN_MODE         = "manual"
AUTO_FILTER       = True
DC_TRACKING       = True      #DC offset tracking
BB_TRACKING       = True      #Baseband tracking
QUADRA_TRACKING   = True     # quadrature tracking
ATTENUATION       = 0
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
