import numpy
from gnuradio import gr, blocks, fft, analog
from gnuradio import digital 
import settings 
import helpers
import parameters_ofdm as para 
import tagger 
import framer
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
		#tag the received bytes
        tagger_0  = tagger.blk(settings.PAYLOAD_BPS, settings.LENGTH_TAG_KEY,1,0) #divides the incoming byte stream into packets and append the meta data 
	"""
            this part will handle the header stream
            from the tagged data stream the header is derived, scrambled and modulated
        """
        header_gen = ownHeader.generate_header_bb(settings.LENGTH_TAG_KEY) #geneating the header
        scramblerH = digital.digital.additive_scrambler_bb(     #srambling the header bytes
			0x8a,
			settings.SCRAMBLED_SEED,
			7,
			0,
			bits_per_byte = 8,
			reset_tag_key = settings.LENGTH_TAG_KEY
		)
        """
            Modulating the data: first split the bytes into the size of the symbols (unpackerH) then transform the smaller groups of bits into the complex symbols
        """
        unpackerH = blocks.repack_bits_bb(  
			8,
			settings.HEADER_BPS,
			settings.LENGTH_TAG_KEY
        )
        modulatorH = digital.chunks_to_symbols_bc(self.constellationH.points())
	"""
            This part wil handle the data stream
            first a error detection code is appended to stream, then the data is scrambled, and modulated to complex symbols 
        """
        crc       = digital.crc32_bb(False, settings.LENGTH_TAG_KEY) #error detection
        scrambler = digital.digital.additive_scrambler_bb(           #scrambling
			0x8a,
			settings.SCRAMBLED_SEED,
			7,
			0,
			bits_per_byte = 8,
			reset_tag_key = settings.LENGTH_TAG_KEY
		)
        """
            modulation: split into a group of bits with convenient size, transform the smaller groups into the complex symbols
        """
        unpacker = blocks.repack_bits_bb(
			8,
			settings.PAYLOAD_BPS,
			settings.LENGTH_TAG_KEY
		)
        modulator = digital.chunks_to_symbols_bc(self.constellationP.points())
	"""
            This part will handle the full ofdm frame, both data, header and preamble 
            first the payload and the header stream is combined, then the complex symbols are allocated the carrier tones and the pilot symbols are append and the preambles is inserted 
            Thereafter, the FFT is calculated, at last the cyclic prefixes are inserted
        """
        header_payload_mux = blocks.tagged_stream_mux(
			itemsize=gr.sizeof_gr_complex*1,
			lengthtagname = settings.LENGTH_TAG_KEY,
			tag_preserve_head_pos=1
        )
        #self.connect(modulator, blocks.tag_debug(gr.sizeof_gr_complex, "tagsmod"))
		#gerating ofdm signals
        allocator = digital.ofdm_carrier_allocator_cvc(
            symbol_settings.get_fft_length(),
            occupied_carriers=symbol_settings.get_carrier_tones(),
            pilot_carriers   =symbol_settings.get_pilot_tones(),
            pilot_symbols    = SYM_PILOT,
            sync_words       = self.sync_words,
            len_tag_key      =settings.LENGTH_TAG_KEY
        )
        #self.connect(allocator, blocks.tag_debug(gr.sizeof_gr_complex*symbol_settings.get_fft_length(), "tagsalocator"))
        fft_ex = fft.fft_vcc(
			symbol_settings.get_fft_length(),
			False, 
			(),
			True
		)
        prefixer = digital.ofdm_cyclic_prefixer(
			symbol_settings.get_fft_length(),
			symbol_settings.get_cp_length() + symbol_settings.get_fft_length(),
			0,
			settings.LENGTH_TAG_KEY
		)
        print("All blocks initialized correctly")
        self.connect(self, tagger_0)
        self.connect(
			tagger_0, 
			header_gen,
			scramblerH,
			unpackerH,
			modulatorH,
			(header_payload_mux,0)
		)	
        self.connect(
			tagger_0,
			crc,
			scrambler,
			unpacker,
			modulator,
			(header_payload_mux,1)
        )
        self.connect(
			header_payload_mux,
			allocator,
			fft_ex,			
			prefixer,
			self
		)
        #self.connect(prefixer, blocks.file_sink(gr.sizeof_gr_complex,"tx.dat"))
        print("All blocks properly connected")
	#self.connect(header_gen, blocks.file_sink(1,'header.txt')) 
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
		detector  = digital.ofdm_sync_sc_cfb(symbol_settings.get_fft_length(), symbol_settings.get_cp_length(), True)
                self.connect((detector,0), blocks.file_sink(gr.sizeof_float, "offset.dat"))
		delayer    = blocks.delay(gr.sizeof_gr_complex, symbol_settings.get_time_length_of_symbol()+5)
		oscillator = analog.frequency_modulator_fc(-2.0 / symbol_settings.get_fft_length())
		splitter   = digital.header_payload_demux(
					3,
					symbol_settings.get_fft_length(), symbol_settings.get_cp_length(),
					settings.LENGTH_TAG_KEY,
					"",
					True,
		)
		mixer      = blocks.multiply_cc()
                self.connect(mixer, blocks.file_sink(gr.sizeof_gr_complex,"mixer_output.dat"))
		header_fft = fft.fft_vcc(symbol_settings.get_fft_length(), True, (), True)
		chanest    = digital.ofdm_chanest_vcvc(SYNC_ONE,SYNC_TWO, 1)
		#self.connect((chanest, 1),blocks.file_sink(gr.sizeof_gr_complex * symbol_settings.get_fft_length(), 'channel-estimate.dat'))
		header_equalizer     = digital.ofdm_equalizer_simpledfe(
                    symbol_settings.get_fft_length(),
                    self.constellationH.base(),
                    symbol_settings.get_carrier_tones(),
                    symbol_settings.get_pilot_tones(),
                    SYM_PILOT,
                    symbols_skipped=0,
		)
		header_eq = digital.ofdm_frame_equalizer_vcvc(
                    header_equalizer.base(),
                    symbol_settings.get_cp_length(),
                    settings.LENGTH_TAG_KEY,
                    True,
                    1 # Header is 1 symbol long
                )
		header_serializer = digital.ofdm_serializer_vcc(
                    symbol_settings.get_fft_length(), symbol_settings.get_carrier_tones(),
                    settings.LENGTH_TAG_KEY
		)
		header_demod     = digital.constellation_decoder_cb(self.constellationH .base())
		header_repack    = blocks.repack_bits_bb(settings.HEADER_BPS, 8, settings.LENGTH_TAG_KEY, True)
		scramblerH = digital.digital.additive_scrambler_bb(
			0x8a,
			settings.SCRAMBLED_SEED,
			7,
			0,
			bits_per_byte = 8,
			reset_tag_key = settings.LENGTH_HEADER_KEY
		)
                self.connect(scramblerH, blocks.file_sink(gr.sizeof_char, "header.dat"))
		parser      = ownHeader.parse_header_bb(settings.LENGTH_HEADER_KEY, settings.LENGTH_TAG_KEY,3,1,0)
		framer_0    = framer.blk(6,settings.LENGTH_HEADER_KEY)
		sender      = ownHeader.send_to_multiplexer_b(settings.LENGTH_HEADER_KEY)
		payload_fft = fft.fft_vcc(symbol_settings.get_fft_length(), True, (), True)
		payload_equalizer = digital.ofdm_equalizer_simpledfe(
                    symbol_settings.get_fft_length(),
                    self.constellationP.base(),
                    symbol_settings.get_carrier_tones(),
                    symbol_settings.get_pilot_tones(),
                    SYM_PILOT,
                    symbols_skipped=1, # (that was already in the header)
                    alpha=0.1
		)
                #self.connect(mixer, blocks.tag_debug(gr.sizeof_gr_complex, "header"))
                #self.connect(payload_fft, blocks.tag_debug(gr.sizeof_gr_complex*64, "payload"))
		payload_eq = digital.ofdm_frame_equalizer_vcvc(
                    payload_equalizer.base(),
                    symbol_settings.get_cp_length(),
                    settings.LENGTH_TAG_KEY
		)
		payload_serializer = digital.ofdm_serializer_vcc(
                    symbol_settings.get_fft_length(), symbol_settings.get_carrier_tones(),
                    settings.LENGTH_TAG_KEY,
                    settings.LENGTH_PACKET_KEY,
                    1 # Skip 1 symbol (that was already in the header)
		)
		payload_demod = digital.constellation_decoder_cb(self.constellationP.base())
		payload_descrambler = digital.additive_scrambler_bb(
                    0x8a,
                    settings.SCRAMBLED_SEED,
                    7,
                    0, # Don't reset after fixed length
                    bits_per_byte=8, # This is after packing
                    reset_tag_key=settings.LENGTH_PACKET_KEY
                )   
		payload_pack = blocks.repack_bits_bb(settings.PAYLOAD_BPS, 8, settings.LENGTH_PACKET_KEY, True)
                crc = digital.crc32_bb(True, settings.LENGTH_PACKET_KEY)
                gate = blocks.tag_gate(gr.sizeof_gr_complex,False)
                """
                    detecting the the preamble
                """
		self.connect(self,detector)
		self.connect(self,delayer, (mixer,0))
                self.connect(gate,(splitter,0))
                self.connect(mixer, gate)
                #self.connect(delayer, (splitter,0)) 
		self.connect((detector,0), oscillator, (mixer,1))
		self.connect((detector,1),(splitter,1))
		#header handling stream
                """
                parse the header data
                """
		self.connect((splitter,0), 
			      header_fft,
			      chanest,
			      header_eq,
			      header_serializer,
			      header_demod,
			      header_repack,
                              framer_0,
			      scramblerH,
			      parser,
			      sender) 
		self.msg_connect(sender, "header", splitter, "header_data") #feedback to the demux 
		#data handler stream
                """
                    retrieve the data
                """
                self.connect((splitter,1), 
				payload_fft,
				payload_eq,
				payload_serializer,
				payload_demod,
				payload_pack,
				payload_descrambler,
				crc, 
				self)
                #self.connect(scramblerH, blocks.file_sink(1,'post-payload-pack.txt')) 
                #self.msg_connect(sender, "header", blocks.message_debug(), "print")
