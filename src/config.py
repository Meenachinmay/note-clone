import os
import yaml

def load_config():
    """Load configuration YAML based on APP_ENVIRONMENT env var."""
    env = os.getenv("APP_ENVIRONMENT", "local")
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", f"{env}.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

ENV_NAME = os.getenv("APP_ENVIRONMENT", "local")
config = load_config()
