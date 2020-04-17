import numpy as np
from gnuradio import gr
import pmt 


SYMBOL_LENGTH = 6
BYTE = 255
class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, header_length, len_tag_key = "header_len"):  # only default arguments here
        gr.sync_block.__init__(
            self,
            name='Tagger',   # will show up in GRC
            in_sig = [np.byte],
            out_sig= [np.byte]
        )
	self.header_length =header_length
	self.len_tag_key = len_tag_key
    def work(self, input_items, output_items):
        number_of_consumed_items = len(output_items[0])
        for index in range(number_of_consumed_items):
            if (self.nitems_written(0) + index)%self.header_length==0:
                self.add_item_tag(0,self.nitems_written(0)+index,pmt.intern(self.len_tag_key),pmt.from_long(self.header_length))
        output_items[0][:] = input_items[0]
        return number_of_consumed_items
		
		
