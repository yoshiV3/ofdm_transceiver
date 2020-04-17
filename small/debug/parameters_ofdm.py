import settings 
import random 
import numpy
import helpers
class ofdm_symbol:
	def __init__(self):
		print('generating settings for ofdm symbol')
		self._data_tones = settings.TONES_NEGATIVE + settings.TONES_POSITIVE
	def get_fft_length(self):
		return settings.FFT_LENGTH
	def get_cp_length(self):
		return settings.CP_LENGTH
	def get_time_length_of_symbol(self):
		return self.get_fft_length() + self.get_cp_length()
	def get_carrier_tones(self):
		return (self._data_tones,)
	def get_pilot_tones(self):
		return (settings.PILOT_TONES,)
	def get_active_tones(self):
		active = list()
		for tone in settings.TONES_NEGATIVE + settings.TONES_POSITIVE + settings.PILOT_TONES:
			if tone < 0:
				active.append(tone + self.get_fft_length())
			else: 
				active.append(tone)
		active.sort() 
		return active
	def _generate_sync_word_one(self):
		random.seed(settings.SYNC_SEED)
		active_tones = self.get_active_tones()
		sw1 = [numpy.sqrt(2)*helpers.mapper_bpsk(random.getrandbits(1)) if x%2 == 0 and x in active_tones else 0 for x in range(self.get_fft_length())]
		print(sw1)
		return numpy.fft.fftshift(sw1)
	def _generate_sync_word_two(self):
		random.seed(settings.SYNC_SEED)
		active_tones = self.get_active_tones()
		sw2 = [helpers.mapper_bpsk(random.getrandbits(1)) if x in active_tones else 0 for x in range(self.get_fft_length())]
		print(sw2) 
		sw2[0] = 0j
		return numpy.fft.fftshift(sw2)
	def _generate_pilot_symbols(self):
		randomSEQUENCE = helpers.get_random_sequence_for_pilot(settings.PILOT_SEQ_LENGTH)
		return tuple([(-x, x, x, -x) for x in randomSEQUENCE ])
		