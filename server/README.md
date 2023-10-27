This directory contains the server-side code
for the Iroha news mailer, that's supposed to be running in Docker.
Current version is available at the [`iroha_mailer`](https://hub.docker.com/r/iamgrid/iroha_mailer) [DockerHub](https://hub.docker.com) repository.

It depends on:

* a TOML configuration file
* a list of subscribers in `yaml` format
* a `secret` file for the OTP feature (can be generated on the server side)

# Configuration structure

The configuration is split on three sections, `http`, `smtp`, `mail`.

The `http` section configures an internal HTTP server, which is used
for the subscription frontend and the API.

The `smtp` section lets you configure the `SMTP` connection and nothing else.
Please take note that the `from` field can be overridden in other section, `mail`.

The `mail` section allows you configure the key things, related to your email:

* `email_from` overrides your email address, which can be useful when you need to use an email alias
* `root_url` sets a root URL of the mailer server, so that an unsubscription feature can work properly
* `enable_list_unsibscribe` parameter lets you
   enable or disable [`list-unsubscribe`](https://www.ietf.org/rfc/rfc2369.txt) header for your emails,
   which is useful for SEO.

```toml
[http]
port = 8080
host = "0.0.0.0"

[smtp]
host = 'smtp.gmail.com'
isSSL = true
user = 'mailer@company.org'
password = 'YOUR_PASS'

[mail]
email_from = 'mailer_address@test_mailer.org'
root_url = "test_mailer.org"
enable_list_unsubscribe = true
```

# Container-related commands

These are the commands used to configure Docker as expected.

The commands are here for the demonstration and aren't
different from the normal use of Docker.

`build` and `push` commands are using version `0.1` for the example.

## Building a container

```bash
docker buildx build . --tag 'iamgrid/iroha_mailer:v0.1'
```

## Running a container

```bash
docker run \
       --init --expose 8080 \
       -p 8080:8080 \
       -p 465:465 \
       -v ./config/config.toml:/etc/mailer/config.toml \
       -v ./config/emails.yaml:/etc/mailer/emails.yaml \
       -v ./config/secret.txt:/run/secrets/mailer_secret \
       'iamgrid/iroha_mailer:v0.1'
```

## Pushing an updated container

```bash
docker push 'iamgrid/iroha_mailer:v0.1'
```