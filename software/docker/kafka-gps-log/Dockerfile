FROM python:3.7

WORKDIR /usr/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./kafka-gps-log.py .
COPY ./gps.avsc .

CMD ["./kafka-gps-log.py"]
