#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: RTL-SDR FM Tuner
# GNU Radio version: 3.10.1.0

from gnuradio import analog
from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import network
import avena_fm_demo_epy_block_0 as epy_block_0  # embedded python block
import avena_fm_demo_epy_block_1 as epy_block_1  # embedded python block
import avena_fm_demo_epy_block_3 as epy_block_3  # embedded python block
import osmosdr
import time




class avena_fm_demo(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "RTL-SDR FM Tuner", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1e06
        self.volume = volume = 1
        self.transition_bw = transition_bw = 10e3
        self.stream = stream = False
        self.sdr_gain = sdr_gain = 10
        self.quadrature = quadrature = samp_rate/4
        self.min_buff = min_buff = 0
        self.max_buff = max_buff = 0
        self.ft = ft = 98.7e06
        self.fft_size = fft_size = 1024
        self.fc = fc = 98.7e06
        self.decimation = decimation = 4
        self.cutoff = cutoff = 100000.0
        self.audio_rate = audio_rate = 44000

        ##################################################
        # Blocks
        ##################################################
        self.rtlsdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + ''
        )
        self.rtlsdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.rtlsdr_source_0.set_sample_rate(samp_rate)
        self.rtlsdr_source_0.set_center_freq(ft, 0)
        self.rtlsdr_source_0.set_freq_corr(0, 0)
        self.rtlsdr_source_0.set_dc_offset_mode(0, 0)
        self.rtlsdr_source_0.set_iq_balance_mode(0, 0)
        self.rtlsdr_source_0.set_gain_mode(False, 0)
        self.rtlsdr_source_0.set_gain(sdr_gain, 0)
        self.rtlsdr_source_0.set_if_gain(20, 0)
        self.rtlsdr_source_0.set_bb_gain(20, 0)
        self.rtlsdr_source_0.set_antenna('', 0)
        self.rtlsdr_source_0.set_bandwidth(0, 0)
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=int(audio_rate/10000*samp_rate/200000),
                decimation=int(samp_rate/40000),
                taps=[],
                fractional_bw=0)
        self.network_udp_sink_0 = network.udp_sink(gr.sizeof_float, 1, '127.0.0.1', 2000, 0, 1472, False)
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(decimation,  firdes.complex_band_pass(1, samp_rate, -samp_rate/(2*decimation), samp_rate/(2*decimation), transition_bw), ft-fc, samp_rate)
        self.fft_vxx_0 = fft.fft_vcc(fft_size, True, window.blackmanharris(fft_size), True, 1)
        self.epy_block_3 = epy_block_3.blk(scale=10000, vector_size=fft_size)
        self.epy_block_1 = epy_block_1.blk(nats_server='nats://localhost:4222', subject='sdr.control')
        self.epy_block_0 = epy_block_0.blk(vector_size=fft_size, subject='sdr.fft', nats_server='nats://localhost:4222', freq=fc, span=samp_rate, stream=stream, gain=sdr_gain)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_selector_0 = blocks.selector(gr.sizeof_gr_complex*1,0,0)
        self.blocks_selector_0.set_enabled(False)
        self.blocks_null_source_0 = blocks.null_source(gr.sizeof_gr_complex*1)
        self.blocks_msgpair_to_var_1 = blocks.msg_pair_to_var(self.set_stream)
        self.blocks_msgpair_to_var_0_1 = blocks.msg_pair_to_var(self.set_ft)
        self.blocks_msgpair_to_var_0_0 = blocks.msg_pair_to_var(self.set_sdr_gain)
        self.blocks_msgpair_to_var_0 = blocks.msg_pair_to_var(self.set_fc)
        self.blocks_moving_average_xx_0 = blocks.moving_average_cc(256, 1.0/256.0, 1, fft_size)
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_gr_complex*fft_size, 256)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(fft_size)
        self.analog_wfm_rcv_0 = analog.wfm_rcv(
        	quad_rate=quadrature,
        	audio_decimation=int(samp_rate/200000),
        )


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.epy_block_1, 'Center Frequency'), (self.blocks_msgpair_to_var_0, 'inpair'))
        self.msg_connect((self.epy_block_1, 'Gain'), (self.blocks_msgpair_to_var_0_0, 'inpair'))
        self.msg_connect((self.epy_block_1, 'Frequency'), (self.blocks_msgpair_to_var_0_1, 'inpair'))
        self.msg_connect((self.epy_block_1, 'Stream Status'), (self.blocks_msgpair_to_var_1, 'inpair'))
        self.msg_connect((self.epy_block_1, 'Stream Control'), (self.blocks_selector_0, 'en'))
        self.connect((self.analog_wfm_rcv_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.epy_block_3, 0))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.blocks_moving_average_xx_0, 0), (self.blocks_keep_one_in_n_0, 0))
        self.connect((self.blocks_null_source_0, 0), (self.epy_block_1, 0))
        self.connect((self.blocks_selector_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.epy_block_3, 0), (self.epy_block_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_moving_average_xx_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.analog_wfm_rcv_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.network_udp_sink_0, 0))
        self.connect((self.rtlsdr_source_0, 0), (self.blocks_selector_0, 0))
        self.connect((self.rtlsdr_source_0, 0), (self.blocks_stream_to_vector_0, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_quadrature(self.samp_rate/4)
        self.epy_block_0.span = self.samp_rate
        self.freq_xlating_fir_filter_xxx_0.set_taps( firdes.complex_band_pass(1, self.samp_rate, -self.samp_rate/(2*self.decimation), self.samp_rate/(2*self.decimation), self.transition_bw))
        self.rtlsdr_source_0.set_sample_rate(self.samp_rate)

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume

    def get_transition_bw(self):
        return self.transition_bw

    def set_transition_bw(self, transition_bw):
        self.transition_bw = transition_bw
        self.freq_xlating_fir_filter_xxx_0.set_taps( firdes.complex_band_pass(1, self.samp_rate, -self.samp_rate/(2*self.decimation), self.samp_rate/(2*self.decimation), self.transition_bw))

    def get_stream(self):
        return self.stream

    def set_stream(self, stream):
        self.stream = stream
        self.epy_block_0.stream = self.stream

    def get_sdr_gain(self):
        return self.sdr_gain

    def set_sdr_gain(self, sdr_gain):
        self.sdr_gain = sdr_gain
        self.epy_block_0.gain = self.sdr_gain
        self.rtlsdr_source_0.set_gain(self.sdr_gain, 0)

    def get_quadrature(self):
        return self.quadrature

    def set_quadrature(self, quadrature):
        self.quadrature = quadrature

    def get_min_buff(self):
        return self.min_buff

    def set_min_buff(self, min_buff):
        self.min_buff = min_buff

    def get_max_buff(self):
        return self.max_buff

    def set_max_buff(self, max_buff):
        self.max_buff = max_buff

    def get_ft(self):
        return self.ft

    def set_ft(self, ft):
        self.ft = ft
        self.freq_xlating_fir_filter_xxx_0.set_center_freq(self.ft-self.fc)
        self.rtlsdr_source_0.set_center_freq(self.ft, 0)

    def get_fft_size(self):
        return self.fft_size

    def set_fft_size(self, fft_size):
        self.fft_size = fft_size
        self.epy_block_0.vector_size = self.fft_size

    def get_fc(self):
        return self.fc

    def set_fc(self, fc):
        self.fc = fc
        self.epy_block_0.freq = self.fc
        self.freq_xlating_fir_filter_xxx_0.set_center_freq(self.ft-self.fc)

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation
        self.freq_xlating_fir_filter_xxx_0.set_taps( firdes.complex_band_pass(1, self.samp_rate, -self.samp_rate/(2*self.decimation), self.samp_rate/(2*self.decimation), self.transition_bw))

    def get_cutoff(self):
        return self.cutoff

    def set_cutoff(self, cutoff):
        self.cutoff = cutoff

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate




def main(top_block_cls=avena_fm_demo, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    tb.wait()


if __name__ == '__main__':
    main()
