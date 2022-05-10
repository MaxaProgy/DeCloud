FROM python:3.7

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/
COPY . /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3.7", "pool.py"]