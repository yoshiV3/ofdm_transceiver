import random
import settings
from gnuradio import digital
def mapper_bpsk(bps):
	map = {
		0:-1,
		1:1
	}
	return map[bps]
def get_random_sequence_for_pilot(number_of_bits):
    RANDOM_BIT_COUNT = number_of_bits
    result = []
    random.seed(settings.PILOT_SEED)
    for bit in range(RANDOM_BIT_COUNT):
        random_bit = random.getrandbits(1)
        result.append(mapper_bpsk(random_bit))
    return result	
def get_constellation(bps):
	map = {
		1:digital.constellation_bpsk(),
		2:digital.constellation_qpsk(),
		3:digital.constellation_8psk()
	}
	return map[bps]