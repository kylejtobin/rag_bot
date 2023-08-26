import yaml
from dotenv import load_dotenv
import os
from pathlib import Path
def load_config():
    # Find the project root based on the location of this file
    project_root = Path(__file__).resolve().parents[2]
    config_file_path = project_root.joinpath("config.yml")
    
    with open(config_file_path, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return config

def setup_environment_variables(config):
    load_dotenv(config["Key_File"])
    openai_api_key = os.getenv('OPENAI_API_KEY')
    serpapi_api_key = os.getenv('SERPAPI_API_KEY')

    if openai_api_key is not None:
        os.environ['OPENAI_API_KEY'] = openai_api_key

    if serpapi_api_key is not None:
        os.environ['SERPAPI_API_KEY'] = serpapi_api_key
