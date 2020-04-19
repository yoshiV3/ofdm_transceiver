"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr
import pmt 
import random
import settings

class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Source',   # will show up in GRC
            in_sig = None,
            out_sig=[np.byte]
        )
	self.p_len       = settings.p_len_tag_key
	self.p_length    = settings.PACKET_LENGTH
	self.pmt_length  = pmt.from_long(self.p_length)
	self.receiver    = pmt.from_long(settings.node2) 
	self.pay         = pmt.from_long(settings.NB_OF_SYMBOLS_PER_FRAME)
	self.d_len       = settings.payload_len_key
	self.r_key       = settings.receiver_key
# if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).

    def work(self, input_items, output_items):
        """example: multiply with constant"""
        for index in range(len(output_items[0])):
        	abs_ind = index + self.self.nitems_written(0)
            	output_items[0][index] = random.getrandbits(8)
            	if abs_ind%self.p_length ==0: 
    			self.add_item_tag(0, abs_ind, self.p_len)
			self.add_item_tag(0, abs_ind, self.d_len, self.pay)
			self.add_item_tag(0, abs_ind, self.r_key, self.receiver)
        return len(output_items[0])
