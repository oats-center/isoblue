FROM python:3.7

WORKDIR /usr/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./engine-rpm-pub.py .
COPY ./raw-can.avsc .

CMD ["./engine-rpm-pub.py"]
