## Configuring Google Cloud for the mailer

This article is based on Google's [one](https://developers.google.com/gmail/api/quickstart/python) with the additional details that may be useful during the setup.

### Creating a project

First, you need to create a custom project in Google Cloud.
Visit the [Google Cloud console](https://console.cloud.google.com/projectcreate) and provide specific details about the project:

* Fill out the name of the project. The name isn't checked by the program, so pick a convenient one.
* Select the organization it is affiliated with.

### Configuring Google Cloud: OAuth consent

Begin by navigating to the 'APIs & Services' section, which is found under the menu.

Locate and select the [`OAuth consent screen`](https://console.cloud.google.com/apis/credentials/consent) option and select the user type for your application.

Proceed by clicking on 'Create'. This action leads you to an app registration form.

Fill the form with all the required details. After filling out the form, click 'Save and Continue' to move forward.

The next step involves adding scopes, but in this instance, you will skip this part. Instead, directly click 'Save and Continue' to bypass this step and proceed with the setup process.

### Configuring Google Cloud: OAuth credentials

Using OAuth helps one use Google Cloud services securely.

To configure OAuth credentials in the Google Cloud console, one must first access the [`Credentials`](https://console.cloud.google.com/apis/credentials) page, which also can be found by navigating through `Menu` and then selecting `APIs & Services`.

Once there, click on `Create Credentials`, followed by selecting `OAuth client ID`. Next, choose `Application type` and select `Desktop app`.
You are then required to enter a name for the credential in the `Name` field.
It is important to note that this name is only for reference within the Google Cloud console and does not impact the credential's functionality. After entering the name, click `Create`.
A confirmation screen will then display your new `Client ID` and `Client secret`.

Confirm the creation by clicking `OK`.
This newly created credential will then be listed under `OAuth 2.0 Client IDs`.

Download the JSON file that contains the credential details.
Rename this file to `credentials.json`.

### Setting up and running the initialisation script

Make sure that Python 3 is installed on your system. Check by running `python --version` command in your terminal.

Select and open a directory where the setup script will be loaded.

Create a virtual environment for this setup by from the terminal:

`python -m venv gmail_api_init`.

Clone the current project repository inside the directory.

Change the directory by typing `cd util`.

Install the packages listed in `requirements.txt`: `pip install -r requirements.txt`.

In some instances, you may encounter issues with package installation. To resolve these, try to install the newest requirement versions manually:

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

Copy the credentials file you download from Google to the `gmail_credentials.json` in `util` directory.

Next, run the `gmail_token_setup` script to initialize the GMail access

```
python gmail_token_setup.py --credential_file ./gmail_credentials.json
```

You will see your browser open a new page. Confirm the GMail access there.

This will complete the setup and configuration required for the project in the dev version, i.e. write both `gmail_credentials.json` and `gmail_token.json` in the `server/config` directory.
