# Sender CI utilities

## Request utility

The request utility is supposed to work in CI,
so that a fresh news file can be sent automatically.

It uses TOTP for security and can also be called manually:

```bash
python requester.py \
       -s ../server/config/secret.txt \
       -a "http://ADDR:PORT/schedule" \
       -d ../config/news.toml
```

* `-s` option selects the TOTP `secret` file
* `-a` option sets an address to send the data to
* `-d` option selects the `toml` file with the news to be sent

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
