import numpy
from gnuradio import gr, blocks, fft, analog
from gnuradio import digital 
import settings 
import helpers
import parameters_ofdm as para

class receiver(gr.hier_block2):
	def __init__(self):
		gr.hier_block2.__init__(self, "ofdm_tx",
					gr.io_signature(1, 1, gr.sizeof_gr_complex),
					gr.io_signature(1, 1, gr.sizeof_char))
		symbol_settings     = para.ofdm_symbol()
        self.constellationP = helpers.get_constellation(settings.PAYLOAD_BPS)
        self.constellationH = helpers.get_constellation(settings.HEADER_BPS)
		detector  = digital.ofdm_sync_sc_cfb(symbol_settings.get_fft_length(), symbol_settings.get_cp_length())
		delayer    = blocks.delay(gr.sizeof_gr_complex, symbol_settings.get_time_length_of_symbol)
		oscillator = analog.frequency_modulator_fc(-2.0 / symbol_settings.get_fft_length())
		splitter   = digital.header_payload_demux(
					3,
					symbol_settings.get_fft_length(), symbol_settings.get_cp_length(),
					settings.LENGTH_TAG_KEY,
					"",
					True
		)
		mixer      = blocks.multiply_cc()
		header_fft = fft.fft_vcc(symbol_settings.get_fft_length(),, True, (), True)
		chanest    = digital.ofdm_chanest_vcvc(symbol_settings._generate_sync_word_one(),symbol_settings._generate_sync_word_two(), 1)
		header_equalizer     = digital.ofdm_equalizer_simpledfe(
            symbol_settings.get_fft_length(),,
            self.constellationH.base(),
            symbol_settings.get_carrier_tones(),
            symbol_settings.get_pilot_tones(),
            symbol_settings._generate_pilot_symbols(),
            symbols_skipped=0,
		)
		self.connect(self,detector)
		self.connect(self,delay, (mixer,0), (splitter,0))
		self.connect((detector,0), oscillator, (mixer,1))
		self.connect((detector,1),(splitter,1))
		