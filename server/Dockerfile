FROM python:3.11-slim

WORKDIR /opt/mailer

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY *.py config_schema.json .
COPY templates templates

RUN useradd -ms /bin/bash mailer && \
    chmod +x server.py

USER mailer

EXPOSE 8080
EXPOSE 465

ENV PYTHONUNBUFFERED 1

HEALTHCHECK CMD python /opt/mailer/healthcheck.py || exit 1

CMD ["/opt/mailer/server.py", "-c", "/etc/mailer/config.toml", "-e", "/etc/mailer/emails.yaml", "-s", "/run/secrets/mailer_secret"]
