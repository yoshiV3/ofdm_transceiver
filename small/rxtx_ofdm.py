import numpy
from gnuradio import gr, blocks, fft, analog
from gnuradio import digital 
import settings 
import helpers
import parameters_ofdm as para 
import formatter 
import ownHeader

symbol_settings     = para.ofdm_symbol() #object with settings concerning OFDM symbols
SYNC_ONE            = symbol_settings._generate_sync_word_one() #generating the first sync word
SYNC_TWO            = symbol_settings._generate_sync_word_two() #generating the second sync word
SYM_PILOT           = symbol_settings._generate_pilot_symbols() #generating the thrid sync word

"""
    hierarchical block that generates the OFDM frames and symbols 
     takes the data in bytes and outputs the complex signal that can be transmitted (by the Pluto sdr)
     The incoming stream is split into two streams: a stream for the headers and a stream for the data 
"""
class transmitter(gr.hier_block2):
	def __init__(self):
        	gr.hier_block2.__init__(self, "ofdm_tx",
					gr.io_signature(1, 1, gr.sizeof_char),
                    			gr.io_signature(1, 1, gr.sizeof_gr_complex))
		self.constellationP = helpers.get_constellation(settings.PAYLOAD_BPS)
		self.constellationH = helpers.get_constellation(settings.HEADER_BPS)
		self.sync_words      = [SYNC_ONE,SYNC_TWO]
		#############################################
		#####    DATA LINK LAYER PACKETS    #########
		#############################################
		#error detection
		self.crc              = digital.crc32_bb(False, settings.p_len_tag_key 
		self.connect(self.to_packet_0, self.crc)
		#scramblig of the dara
		self.scrambler= digital.digital.additive_scrambler_bb( 
				0x8a,
				settings.SCRAMBLED_SEED,
				7,
				0,
				bits_per_byte = 8,
				reset_tag_key = settings.p_len_tag_key
			)
		self.connect(self.crc, self.scrambler)
		########################################################################
		#####    DATA LINK LAYER PACKETS   TO PHYSICAL LAYER (FRAME  #########
		########################################################################
		self.to_frame_0 = formatter.transformer_block()
		self.connect(self.scrambler, self.to_frame_0)
		#############################################
		#####    PHYSICAL LAYER FRAMES       #########
		#############################################
		#genereate header stream
		self.header_gen_0 = ownHeader.generate_short_bb(settings.f_len_tag_key,settings.payload_len_key, settings.receiver_key)
		self.connect(self.to_frame_0,self.header_gen_0)
		######  MODULATION ######
		#unpacking the streams 
		self.unpacker_data_stream   = blocks.repack_bits_bb(    #data
				8,
				settings.PAYLOAD_BPS,
				settings.p_len_tag_key
			)
		self.unpacker_header_stream = blocks.repack_bits_bb( #header
				8,
				settings.HEADER_BPS,
				settings.p_len_tag_key
			)
		self.connect(self.to_frame_0, self.unpacker_data_stream)
		self.connect(self;header_gen_0, self.unpacker_header_stream)
		#unpacket bits to complex 
		self.modulator_header_stream = digital.chunks_to_symbols_bc(self.constellationH.points())
		self.modulator_data_stream = digital.chunks_to_symbols_bc(self.constellationP.points())
		self.connect(self.unpacker_data_stream, self.modulator_data_stream)
		self.connect(self.unpacker_header_stream, self.modulator_header_stream)
		#combining streams
		self.header_payload_mux = blocks.tagged_stream_mux(
				itemsize=gr.sizeof_gr_complex*1,
				lengthtagname = settings.f_len_tag_key,
				tag_preserve_head_pos=1
		)
		self.connect(self.modulator_header_stream, (self.header_payload_mux,0))
		self.connect(self.modulator_data_stream, (self.header_payload_mux,1))
		#allocating data on the carriers 
		self.allocator = digital.ofdm_carrier_allocator_cvc(
		    symbol_settings.get_fft_length(),
		    occupied_carriers=symbol_settings.get_carrier_tones(),
		    pilot_carriers   =symbol_settings.get_pilot_tones(),
		    pilot_symbols    = SYM_PILOT,
		    sync_words       = self.sync_words,
		    len_tag_key      =settings.f_len_tag_key
		)
		self.connect(self.header_payload_mux, self.allocator)
		#FFT
		fft_ex = fft.fft_vcc(
				symbol_settings.get_fft_length(),
				False, 
				(),
				True
			)
		self.connect(self.allocator, self.fft_ex)
		#cyclic prefix
		self.prefixer = digital.ofdm_cyclic_prefixer(
				symbol_settings.get_fft_length(),
				symbol_settings.get_cp_length() + symbol_settings.get_fft_length(),
				0,
				settings.f_len_tag_key
			)       
		self.connect(self.fft_ex, self.prefixer)
		############################################
		#####    DPHYSICAL LAYER SAMPLES  #########
		############################################
		self.connect(self.prefixer, self)
        
"""
Hierarchical block to parse the received data stream 
first we detect the incoming stream, then we correct the frequency offset 
thirdly, we retrieve the header from the incoming stream, parse the header for the meta data
lastly, we retrieve the actual data 
"""
class receiver(gr.hier_block2):
	def __init__(self):
		gr.hier_block2.__init__(self, "ofdm_tx",
					gr.io_signature(1, 1, gr.sizeof_gr_complex),
					gr.io_signature(1, 1, gr.sizeof_char))
		self.constellationP = helpers.get_constellation(settings.PAYLOAD_BPS)
		self.constellationH = helpers.get_constellation(settings.HEADER_BPS)
        	############################################
        	#####    PHYSICAL LAYER SAMPLES  #########
        	############################################
        	#detection of the frames
		self.detector  = digital.ofdm_sync_sc_cfb(symbol_settings.get_fft_length(), symbol_settings.get_cp_length(), True)
        	self.connect(self,self.detector)
        	#delay stream (waiting for detection at tge end of the first preamble 
        	self.delay_element  = blocks.delay(gr.sizeof_gr_complex, symbol_settings.get_time_length_of_symbol()+settings.SAFETY_PADDING)
        	#coarse frequency correction
		self.oscillator = analog.frequency_modulator_fc(-2.0 / symbol_settings.get_fft_length())
		self.connect((self.detector,0), self.oscillator)
		self.mixer   = blocks.multiply_cc()
		self.connect(self.delay_element, (self.mixer,0))
		self.connect(self.oscillator, (self.mixer,0))      
		#######################################################################
		#####    PHYSICAL LAYER SAMPLES to PHYSICAL LAYER FRAMES  #########
		#######################################################################
		self.demuxer = digital.header_payload_demux(
						3,
						symbol_settings.get_fft_length(), symbol_settings.get_cp_length(),
						settings.f_len_tag_key,
						"",
						True,
			)
		self.connect(self.mixer, (self.demuxer,0))
		self.connect((self.detection,1), (self.demuxer,1))
		#######################################################################
		#####    PHYSICAL LAYER FRAMES: HEADER STREAM                 #########
		#######################################################################
		####### retrieve the coeffiencients  of the carriers (time to frequency)
		self.header_fft = fft.fft_vcc(symbol_settings.get_fft_length(), True, (), True)
		self.connect((self.demuxer, 0), self.header_fft)
		####### initial estimate
		self.chanest    = digital.ofdm_chanest_vcvc(SYNC_ONE,SYNC_TWO, 1)
		self.connect((self.header_fft), self.chanest)
		####### header zqualization: correcteffect of channel (fine frequency and multipath effects)
  		header_equalizer     = digital.ofdm_equalizer_simpledfe(
	            symbol_settings.get_fft_length(),
	            self.constellationH.base(),
	            symbol_settings.get_carrier_tones(),
	            symbol_settings.get_pilot_tones(),
	            SYM_PILOT,
	            symbols_skipped=0,
		)
		self.header_eq = digital.ofdm_frame_equalizer_vcvc(
	            header_equalizer.base(),
	            symbol_settings.get_cp_length(),
	            settings.LENGTH_TAG_KEY,
	            True,
	            1 # Header is 1 symbol long
		 )
		 self.connect(self.chanest, self.header_eq)
		 ####### Parallel data on carrriers to serial stream
		 self.header_serializer = digital.ofdm_serializer_vcc(
		            symbol_settings.get_fft_length(), symbol_settings.get_carrier_tones(),
		            settings.f_len_tag_key
			)
		self.connect(self.header_eq, self.header_serializer)
		###############################" DEMODULATION: complex to bytes
			self.header_demod     = digital.constellation_decoder_cb(self.constellationH .base())
			self.header_repack    = blocks.repack_bits_bb(settings.HEADER_BPS, 8, settings.f_len_tag_key, True)
		self.connect(self;header_serializer, self.header_demod, self.header_repack)
		############## PARSE HEADER: from bytes to meta data and instructions for demuxer
		self.framer_0   = framer.blk(1,settings.h_len_tag_key)
			self.parser       = ownHeader.parse_short_bb(settings.h_len_tag_key, settings.f_len_tag_key,settings.nodeOne_ID, settings.maxPayload)
			self.sender      = ownHeader.send_to_multiplexer_b(settings.h_len_tag_key)
		self.connect(self.header_repack, self.framer_0, self.parser, self.send_to_multiplexer_b)
		##### Feedback
		self.msg_connect(self.sender, "header", self.demuxer, "header_data") #feedback to the demux 
		#######################################################################
		#####    PHYSICAL LAYER FRAMES: DATA   STREAM                 #########
		#######################################################################
		###
		####### retrieve the coeffiencients  of the carriers (time to frequency)
		self.payload_fft = fft.fft_vcc(symbol_settings.get_fft_length(), True, (), True)
		self.connect((self.demuxer, 1), self.payload_fft)
		######equalization 
		payload_equalizer = digital.ofdm_equalizer_simpledfe(
                    symbol_settings.get_fft_length(),
                    self.constellationP.base(),
                    symbol_settings.get_carrier_tones(),
                    symbol_settings.get_pilot_tones(),
                    SYM_PILOT,
                    symbols_skipped=1, # (that was already in the header)
                    alpha=0.1
		)
		self.payload_eq = digital.ofdm_frame_equalizer_vcvc(
                    payload_equalizer.base(),
                    symbol_settings.get_cp_length(),
                    settings.f_len_tag_key
		)
		self.connect(self.payload_fft, self.payload_eq)
		####### Parallel data on carrriers to serial stream
		self.payload_serializer = digital.ofdm_serializer_vcc(
                    symbol_settings.get_fft_length(), symbol_settings.get_carrier_tones(),
                    settings.f_len_tag_key,
                    settings.,
                    1 # Skip 1 symbol (that was already in the header)
		)
		self.connect(self.payload_eq, self.payload_serializer)
		###############################" DEMODULATION: complex to bytes
		self.payload_demod = digital.constellation_decoder_cb(self.constellationP.base())  
		self.payload_pack = blocks.repack_bits_bb(settings.PAYLOAD_BPS, 8, settings.LENGTH_PACKET_KEY, True)
		self.connect(self.payload_serializer,self.payload_demod,self.payload_pack)
		#######################################################################
		#####   PHYSICAL LAYER TO DATA LINK LAYER                     #########
		#######################################################################
		self.from_frame_to_packet_0 = formatter.reverse_block()
		self.connect(self.payload_pack, self.from_frame_to_packet_0)
		#######################################################################
		#####   DATA LINK LAYER                                       #########
		#######################################################################	
		### descramble
		self.payload_descrambler = digital.additive_scrambler_bb(
                    0x8a,
                    settings.SCRAMBLED_SEED,
                    7,
                    0, # Don't reset after fixed length
                    bits_per_byte=8, # This is after packing
                    reset_tag_key=settings.p_len_tag_key
                )
                self.connect(self.from_frame_to_packet_0, self.payload_descrambler)
                #### error detection		
                self.crc = digital.crc32_bb(True, settings.p_len_tag_key)
                self.connect(self.payload_descrambler,self.crc)
                #### output
                self.connect(self.crc, self)
