FROM python:3.7

WORKDIR /usr/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./start.sh .
COPY ./kafka-gps-log.py .
COPY ./gps.avsc .

CMD ["./start.sh"]
