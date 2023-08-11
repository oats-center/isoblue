#BUILDER

from python:3 as builder

WORKDIR /usr/src/app

#Download latest listing of available packages

RUN apt-get -y update

RUN apt-get install -y --no-install-recommends python3-pip pkg-config

#Activate virtualenv

RUN python -m venv /opt/venv

#Make sure we use the virtualenv

ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and build with pip
COPY requirements.txt ./
RUN pip install -r requirements.txt


# RUNTIME
FROM python:3 as runtime

WORKDIR /usr/src/app

# Copy compiled venv from builder
COPY --from=builder /opt/venv /opt/venv

# Make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# Copy health check script
COPY healthcheck.py .
HEALTHCHECK CMD ["python", "./healthcheck.py"]

# Copy script over and run
COPY can_logger.py .
CMD [ "./can_logger.py" ]
