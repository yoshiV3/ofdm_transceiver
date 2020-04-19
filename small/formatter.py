import numpy
from gnuradio import gr
import settings
import pmt

class transformer_block(gr.sync_block): 
	"""Embedded Python Block example - a simple multiply const"""

	def __init__(self):  # only default arguments here
		"""arguments to this function show up as parameters in GRC"""
		gr.sync_block.__init__(
		    self,
		    name='Transformer',   # will show up in GRC
		    in_sig = [np.byte],
		    out_sig=[np.byte]
		)
		self.set_tag_propagation_policy(gr.TPP_DONT)
		self.p_len   = settings.p_len_tag_key
		self.f_len   = settings.f_len_tag_key
		self.d_len   = settings.payload_len_key
		self.r_key   = settings.receiver_key
		self.start   = 0
		self.sym_cnt = pmt.from_long(0)
		self.length  = 0
		self.f_value = pmt.from_long(self.length) 
		self.bytes_per_symbol = settings.PAYLOAD_BPS*settings.BYTES_PER_SYM

	def work(self, input_items, output_items):
		"""example: multiply with constant"""
		for index in range(len(output_items[0])):
			abs_ind = index + self.self.nitems_written(0)
			tags = tags = self.get_tags_in_window(1, index, index+1)
			if len(tags) > 2:
				for tag in tags:
					key   =  pmt.to_python(tag.key)
					value =  pmt.to_python(tag.value)
					if key == self.p_len:
						self.start = abs_ind
					elif key == self.d_len:
						self.sym_cnt = pmt.from_long(value)
						self.length  = self.bytes_per_symbol*value
						self.f_value = pmt.from_long(self.length) 
					elif key == self.r_key:
						self.receiver = pmt.from_long(value)
			packet_ind = abs_ind - self.start 
			if packet_ind%self.length ==0:
				self.add_item_tag(0, abs_ind, self.f_len, self.f_value)
				self.add_item_tag(0, abs_ind, self.d_len, self.sym_cnt)
				self.add_item_tag(0, abs_ind, self.r_key, self.receiver)
		output_items[0][:] = input_items[0][:]
		return len(output_items[0])
class reverse_block(gr.sync_block): 
	"""Embedded Python Block example - a simple multiply const"""

	def __init__(self):  # only default arguments here
		"""arguments to this function show up as parameters in GRC"""
		gr.sync_block.__init__(
		    self,
		    name='Reverser',   # will show up in GRC
		    in_sig = [np.byte],
		    out_sig=[np.byte]
		)
		self.set_tag_propagation_policy(gr.TPP_DONT)
		self.p_length      = settings.PACKET_LENGTH + 4 #packet length plus crc bytes
		self.p_value       = pmt.from_long(self.p_length)
		self.p_len_tag_key = settings.p_len_tag_key
		self.p_len         = pmt.intern(self.p_len_tag_key)
	def work(self, input_items, output_items):
		for index in range(len(output_items[0])):
			abs_ind = index + self.self.nitems_written(0)
			if avs_ind%p_length ==0:
				self.add_item_tag(0, abs_ind, self.p_len, self.p_value)
		output_items[0][:] = input_items[0][:]
		return len(output_items[0])			
					
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
										
