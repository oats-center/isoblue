FROM python:3.7

WORKDIR /usr/app

COPY requirements.txt ./

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./kafka-gps-log.py .
COPY ./gps.avsc .
COPY ./start.sh .

CMD ["./start.sh"]
