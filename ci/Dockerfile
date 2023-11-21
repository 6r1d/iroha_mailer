FROM python:3.11-slim

RUN apt-get update && \
    apt-get -y upgrade

RUN mkdir /app
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY *.py .

RUN useradd -ms /bin/bash mailer && \
    chown root:root /app -R && \
    chmod +x request_print.py request_mail.py

USER mailer

CMD ["/app/request_print.py"]