FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY *.py .

RUN useradd -ms /bin/bash mailer && \
    chmod +x request_print.py request_mail.py

USER mailer

CMD ["/app/request_print.py"]