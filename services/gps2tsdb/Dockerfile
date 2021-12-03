FROM python:3

WORKDIR /

# Copy requirements and build with pip
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy script over and run
COPY gps2tsdb.py .
COPY manage_db.py . 
CMD [ "python", "./gps2tsdb.py" ]
