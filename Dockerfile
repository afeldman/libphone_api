FROM python:3.8.13-slim

COPY requirements.txt /tmp/
RUN /usr/local/bin/python3 -m pip install --upgrade pip
RUN pip3 install -r /tmp/requirements.txt

COPY . /app
WORKDIR /app

EXPOSE 8003

ENTRYPOINT ["./gunicorn.sh"]