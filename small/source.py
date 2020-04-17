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
        self.load = 0
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).

    def work(self, input_items, output_items):
        """example: multiply with constant"""
        key   = pmt.intern('packet_len')
        value = pmt.from_long(8)
        for index in range(len(output_items[0])):
            output_items[0][index] = random.getrandbits(8)
        return len(output_items[0])
