# Provides a base Ubuntu (20.04) image with latest UHD installed

FROM        ubuntu:20.04
MAINTAINER  OATS Center

# Last build date - this can be updated whenever there are security updates so
# that everything is rebuilt

ENV         security_updates_as_of 2021-11-01

# This will make apt-get install without question

ARG         DEBIAN_FRONTEND=noninteractive

# Set UHD and GNURadio git tags

ARG         UHD_TAG=v4.1.0.4
ARG         GNU_TAG=v3.9.4.0

# Use 16 threads when compiling

ARG         MAKEWIDTH=16

# Install security updates and required packages

RUN         apt-get update
RUN         apt-get -y install -q \
                build-essential \
                ccache \
                git \
                python3-dev \
                python3-pip \
                curl
# Install UHD and GNURadio dependencies

RUN         apt-get -y install -q \
                libboost-all-dev \
		g++ \
		gir1.2-gtk-3.0 \
                libusb-1.0-0-dev \
                libudev-dev \
                python3-mako \
                doxygen \
                python3-docutils \
                cmake \
		libfftw3-dev \
		libgmp3-dev \
		liblog4cpp5-dev \
		libqwt-qt5-dev \
		python3-click-plugins \
		python3-distutils \
		python3-gi-cairo \
                python3-requests \
                python3-numpy \
	        python3-pyqt5 \
	        python3-pyqtgraph \
	        python3-scipy \
	        python3-yaml \
                dpdk \
                libdpdk-dev \
	        qtbase5-dev \
	        clang-format
RUN          rm -rf /var/lib/apt/lists/*

# Clone UHD repo and build

RUN          mkdir -p /usr/local/src
RUN          git clone https://github.com/EttusResearch/uhd.git /usr/local/src/uhd
RUN          cd /usr/local/src/uhd/ && git checkout $UHD_TAG
RUN          mkdir -p /usr/local/src/uhd/host/build
WORKDIR      /usr/local/src/uhd/host/build
RUN          cmake .. -DENABLE_PYTHON3=ON -DUHD_RELEASE_MODE=release -DCMAKE_INSTALL_PREFIX=/usr
RUN          make -j $MAKEWIDTH
RUN          make install
RUN          uhd_images_downloader

# Install pip dependencies

RUN          pip3 install "pybind11[global]"

# Install Volk
WORKDIR      /usr/local/src
RUN 	     git clone --recursive https://github.com/gnuradio/volk.git && \
	     cd volk && mkdir build && cd build && \
	     cmake -DCMAKE_BUILD_TYPE=Release -DPYTHON_EXECUTABLE=/usr/bin/python3 ../ \
	     && make && make test && make install

# Clone GNURadio repo and build

WORKDIR      /usr/local/src
RUN          git clone --recursive https://github.com/gnuradio/gnuradio 
RUN          cd /usr/local/src/gnuradio && \
             git checkout $GNU_TAG && \
             git submodule update --init --recursive 
RUN          mkdir -p /usr/local/src/gnuradio/build 
WORKDIR      /usr/local/src/gnuradio/build
RUN          cmake ../ 
RUN          make -j $MAKEWIDTH
RUN          make install 
RUN          ldconfig 
RUN          echo 'PYTHONPATH=/usr/local/lib/python3.7/dist-packages' >> /etc/environment

# Set env to find FPGA images and add udev rule to allow normal users access
# USB radios

WORKDIR      /
ENV	     UHD_IMAGES_DIR=/usr/share/uhd/images
RUN          cp /usr/lib/uhd/utils/uhd-usrp.rules /etc/udev/rules.d/10-uhd-usrp.rules
