"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, scale=1, vector_size=1024):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Float to UShort',   # will show up in GRC
            in_sig=[(np.single, vector_size)],
            out_sig=[(np.ushort, vector_size)]
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.scale = scale

    def work(self, input_items, output_items):
        """example: multiply with constant"""
        output_items[0][:] = np.ushort(input_items[0] * self.scale)
        return len(output_items[0])
