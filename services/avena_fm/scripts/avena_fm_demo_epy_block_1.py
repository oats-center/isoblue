
import os
import numpy as np
from gnuradio import gr
import pmt
from pynats2 import NATSClient
import json

class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block

    def __init__(self, nats_server='nats://localhost:4222', 
                 subject='sdr.control'):  # only default arguments here
        gr.sync_block.__init__(
            self,
            name='NATS Subscription',   # will show up in GRC
            in_sig=[np.complex64],
            out_sig=None
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.port_1 = 'Frequency'
        self.port_2 = 'Center Frequency'
        self.port_3 = 'Gain'
        self.port_4 = 'Stream'
        self.subject = os.getenv('HOSTNAME') + '.' + subject
        self.message_port_register_out(pmt.intern(self.port_1))
        self.message_port_register_out(pmt.intern(self.port_2))
        self.message_port_register_out(pmt.intern(self.port_3))   
        self.message_port_register_out(pmt.intern(self.port_4))          
        self.nc = NATSClient(nats_server, socket_timeout=2)
        self.nc.connect()
        self.nc.subscribe(subject=self.subject, callback=self.callback)
        
    
    def callback(self, msg):
	
        nats_msg = json.loads(msg.payload.decode())    
        PMT_msg_1 = pmt.cons(pmt.string_to_symbol('ft'), 
                  pmt.from_long(nats_msg['ft']))
        PMT_msg_2 = pmt.cons(pmt.string_to_symbol('fc'), 
                  pmt.from_long(nats_msg['fc']))
        PMT_msg_3 = pmt.cons(pmt.string_to_symbol('gain'), 
                  pmt.from_long(nats_msg['gain']))
        PMT_msg_4 = pmt.to_pmt(nats_msg['stream'])
        
        self.message_port_pub(pmt.intern(self.port_1), PMT_msg_1)
        self.message_port_pub(pmt.intern(self.port_2), PMT_msg_2)
        self.message_port_pub(pmt.intern(self.port_3), PMT_msg_3)
        self.message_port_pub(pmt.intern(self.port_4), PMT_msg_4)
        
        print(f"Frequency set to {nats_msg['ft']} Hz")
        print(f"Center Frequency set to {nats_msg['fc']} Hz")
        print(f"Gain set to {nats_msg['gain']} dB")
        print(f"Streaming: {nats_msg['stream']}")   
             
    def work(self, input_items, output_items):
        
        return len(input_items[0])
        
        
