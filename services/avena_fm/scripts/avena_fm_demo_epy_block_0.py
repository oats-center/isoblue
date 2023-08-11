import os
import numpy as np
from gnuradio import gr
from pynats2 import NATSClient
import json
from base64 import b64encode, b64decode

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block


    def __init__(self, vector_size=1024, subject='fft', 
                 nats_server='nats://localhost:4222',
                 freq=98700000, span=2000000, stream=False, gain=0):  # only default arguments here

        gr.sync_block.__init__(
            self,
            name='NATS Sink',   # will show up in GRC
            in_sig=[(np.ushort, vector_size)],
            out_sig=None
        )

        avena_prefix = os.getenv('AVENA_PREFIX')
        self.vector_size = vector_size
        self.freq = freq
        self.span = span
        self.stream = stream
        self.gain = gain
        self.subject = subject
        #self.subject = avena_prefix + '.' + subject
        self.nc = NATSClient(nats_server, socket_timeout=2)
        self.nc.connect()
        
    def work(self, input_items, output_items):
        
        b64encpayload = str(b64encode(input_items[0][0]), 'utf-8')
        json_dump = json.dumps({'fft': b64encpayload,
                                'fc' : self.freq,
                                'gain' : self.gain, 
                                'span' : self.span, 
                                'fft_size' : self.vector_size,
                                'stream' : self.stream}, 
                                cls=NumpyEncoder)
        self.nc.publish(subject=self.subject ,payload=json_dump)
        
        return len(input_items[0])
