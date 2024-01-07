# /app/src/utils/config.py

# Utilities
from pathlib import Path
import yaml
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


def load_config() -> dict:
    """
    Load the configuration from a YAML file located in the project root.

    Returns:
        dict: Configuration parameters from the YAML file.
    """

    # Determine the project root based on the current file's location
    project_root = Path(__file__).resolve().parents[2]
    config_file_path = project_root / "config.yml"

    # Safely open and read the configuration file
    with open(config_file_path, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
            return config
        except yaml.YAMLError as exc:
            # Log any errors that occur during YAML parsing
            print(exc)
            return {}  # Return an empty dictionary if an error occurs


def setup_environment_variables(config: dict):
    """
    Load environment variables from the specified key file.

    Args:
        config (dict): Configuration containing the path to the key file.
    """
    load_dotenv(config["Key_File"])
