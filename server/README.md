This directory contains the server-side code
for the Iroha news mailer, that's supposed to be running in Docker.

It depends on:

* a TOML configuration file
* a list of subscribers in `yaml` format
* a `secret` file for the OTP feature (can be generated on the server side)

# Container-related commands

These are the commands used to configure Docker as expected.

## Building a container

```bash
docker buildx build . --tag 'iamgrid/iroha_mailer:v0.1'
```

## Running a container

```bash
docker run \                                           
       --init \
       -p 127.0.0.1:8080:8080 \
       -p 127.0.0.1:465:465 \
       -v ./config/config.toml:/etc/mailer/config.toml \
       -v ./config/emails.yaml:/etc/mailer/emails.yaml \
       -v ./config/secret.txt:/run/secrets/mailer_secret \
       'iamgrid/iroha_mailer:v0.1'
```
