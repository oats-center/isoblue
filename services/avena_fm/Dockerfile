# Use Fedora as base distribution
FROM fedora:36
MAINTAINER 'OATS Center'

# Install updates
RUN dnf -y update; dnf -y clean all

# Install RTL-SDR drivers and GNU Radio
RUN dnf -y install rtl-sdr gnuradio gr-osmosdr

WORKDIR /usr/src/app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy script files
COPY ./scripts/avena_fm_demo.py .
COPY ./scripts/avena_fm_demo_epy_block_0.py .
COPY ./scripts/avena_fm_demo_epy_block_1.py .
COPY ./scripts/avena_fm_demo_epy_block_3.py .

# Run main script
CMD ./scripts/avena_fm_demo.py

