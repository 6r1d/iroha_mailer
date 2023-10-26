"""
This module contains a confugration manager that provides
the configuration validation and getters. 
"""

import sys
from tomllib import load as toml_load
from json import load as json_load
from logging import error, exception
from jsonschema import validate, Draft202012Validator
from jsonschema.exceptions import SchemaError
from filesystem import get_code_dir

class Config:
    """
    Configuration retrieval class.
    """

    def __init__(self, config_path: str):
        """
        Load the configuration, exit if it has issues.

        Args:
            config_path (str): a path to the current TOML config
        """
        self.load_schema()
        self.config = self.load_config(config_path)
        validation_error = self.validate_config(self.config)
        if validation_error:
            error("Improper configuration")
            exception(validation_error)
            sys.exit(1)

    def load_config(self, config_path: str):
        """
        Open and parse the config, report if it has issues.

        Args:
            config_path (str): a path to the current TOML config
        """
        config = {}
        try:
            with open(config_path, "rb") as config_file:
                config = toml_load(config_file)
        except FileNotFoundError:
            error(f"Configuration file not found: {config_path}")
        return config

    def load_schema(self):
        """
        Load a JSON schema for validating the TOML config
        """
        schema_path = get_code_dir() / 'config_schema.json'
        with open(schema_path, encoding='utf-8') as schema_file:
            self.schema = json_load(schema_file)

    def validate_config(self, config):
        """
        An internal function to validate the JSON config.

        Returns:
            None on success, SchemaError instance on validation failure.
        """
        output_error = None
        try:
            validate(
                instance=config,
                schema=self.schema,
                format_checker=Draft202012Validator.FORMAT_CHECKER
            )
        except SchemaError as err:
            output_error = err
        return output_error

    def get_server_options(self):
        """
        Returns:
            (dict): AsyncIO HTTP server options, specifically,
            the host and a port at which the server
            will be running.
        """
        return {
            'host': self.config['http']['host'],
            'port': self.config['http']['port']
        }

    def get_email_from(self):
        """
        Returns:
            (str): the "from" field for an email.
        """
        return self.config['mail']['email_from']

    def get_smtp(self):
        """
        Returns:
            (dict) SMTP server configuration
        """
        return self.config['smtp']

    def get_site_url(self):
        """
        Returns:
            (str / None) site url, needed for the unsubscribe links or None
        """
        return self.config['mail']['root_url'].rstrip('/')

    def check_list_unsubscribe_mode(self):
        """
        Returns:
            (Boolean) returns True if list-unsubscribe header is enabled
        """
        return self.config['mail'].get('enable_list_unsubscribe', False)
