FROM python:3.11-slim

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install nano=7.2-1 --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /opt/mailer
WORKDIR /opt/mailer

COPY requirements.txt .
RUN mkdir -p templates && \
    pip install --no-cache-dir -r requirements.txt
COPY *.py .
COPY config_schema.json .
COPY templates /opt/mailer/templates

RUN useradd -ms /bin/bash mailer && \
    chown mailer:mailer /opt/mailer -R && \
    chown root:root /opt/mailer/*.py && \
    chmod +x server.py

USER mailer

EXPOSE 8080
EXPOSE 465

ENV PYTHONUNBUFFERED 1

HEALTHCHECK CMD python /opt/mailer/healthcheck.py || exit 1

CMD ["/opt/mailer/server.py", "-c", "/etc/mailer/config.toml", "-e", "/etc/mailer/emails.yaml", "-s", "/run/secrets/mailer_secret"]
