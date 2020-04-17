"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr
import pmt 


SYMBOL_LENGTH = 4
BYTE = 255
class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, bps_payload=1, tag_len_key = "packet_len", reiver_id = 1, own_id = 0):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Tagger',   # will show up in GRC
            in_sig = [np.byte],
            out_sig= [np.byte]
        )
        self.n_of_sym   = 1
        self._bytes_p_s = (bps_payload*SYMBOL_LENGTH)
        key_length      = pmt.intern(tag_len_key)
        key_nSymbols    = pmt.intern("number_of_symbols")
        key_seqnum      = pmt.intern("sequence_number")
        key_sendID      = pmt.intern("sender_id")
        key_recvID      = pmt.intern("receiver_id")
        key_padding     = pmt.intern("padding")
        key_mode        = pmt.intern("mode")
        self.keys       = [key_length, key_nSymbols, key_seqnum, key_sendID, key_recvID, key_padding, key_mode]
        recvId          = pmt.from_uint64(reiver_id)
        own_id          = pmt.from_uint64(own_id)
        mode            = pmt.from_uint64(0)
        padding         = pmt.from_uint64(0)
        ZERO            = pmt.from_uint64(0)
        self.seqNum     = 0
        packet_len      = pmt.from_long(self._bytes_p_s*self.n_of_sym)
        num_of_sym      = pmt.from_uint64(self.n_of_sym) 
        self.snInd      = 2
        self.values     = [packet_len,num_of_sym,ZERO,own_id,recvId,padding,mode]
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).

    def work(self, input_items, output_items):
        number_of_consumed_items = len(output_items[0])
        for index in range(number_of_consumed_items):
            if (self.nitems_written(0) + index)%self._bytes_p_s==0:
				for key in range(len(self.keys)):
					self.add_item_tag(0,self.nitems_written(0)+index,self.keys[key],self.values[key])
				self.seqNum = (self.seqNum + 1)%BYTE
				self.values[self.snInd] = pmt.from_uint64(self.seqNum) 
        output_items[0][:] = input_items[0]
        return number_of_consumed_items







				
