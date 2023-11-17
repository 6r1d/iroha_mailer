# Sender CI utilities

## Request utility

The request utility is supposed to work in CI;
it uses TOTP for security and can also be called manually.

There are two options for such request:

* a freshly generated news template can be sent to the subscribers
* a freshly generated news template is saved to a file for a print version

### Email

```bash
python request_mail.py \
       -s ../server/config/secret.txt \
       -a "http://ADDR:PORT/schedule" \
       -d ../config/news.toml
```

* `-s` option selects the TOTP `secret` file
* `-a` option sets an address to send the data to
* `-d` option selects the `toml` file with the news to be sent

### Print version

```bash
python get_print.py \
       -s ../server/config/secret.txt \
       -a "http://ADDR:PORT/generate_print" \
       -d ../config/news.toml \
       -o output.html
```

* `-s` option selects the TOTP `secret` file
* `-a` option sets an address to send the data to
* `-d` option selects the `toml` file with the news to be sent
* `-o` option sets the output file

## TOTP "secret" generator

The secret generator utility is needed for a TOTP secret file generation.
It is shared by the server and a client so that time-based OTP is synced.
You don't need to install dependencies and it was tested on Python 3.11.5.

```bash
# Generate a secret file
python secret_gen.py -s ./random_secret.txt
```

```bash
# Preview the secret file contents
JVXRCQY5GRBEYBY=
```

```bash
# Copy a secret file to the server configuration
cp ./random_secret.txt ../server/config/secret.txt
```

## Example "news" to be sent

Below is a short TOML file reflecting the structure for an email / document render.

```toml
year = "202X"
date = "January X 24, 202X"
title = "Hyperledger Iroha Bi-Weekly News"
delivered = [
    "Delivered feature A",
    "Delivered feature B"
]
current_work = [
    "Feature in development: MacGuffin"
]
planned = [
    "Planned feature 1",
    "Planned feature 2"
]
```