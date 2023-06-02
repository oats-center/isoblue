# BUILDER
FROM python:3.11.3-slim-bullseye as builder

WORKDIR /usr/src/app

# Activate virtualenv
RUN python -m venv /opt/venv

# Make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and build with pip
COPY requirements.txt ./
RUN pip install -r requirements.txt



# RUNTIME
FROM python:3.11.3-slim-bullseye as runtime

WORKDIR /usr/src/app

# Update apt cache

RUN apt-get -y update

# Install FFmpeg and all its dependencies

RUN apt-get install -y --no-install-recommends ffmpeg

# Copy compiled venv from builder
COPY --from=builder /opt/venv /opt/venv

# Make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

COPY avena_video.py .
CMD [ "python", "./avena_video.py" ]
