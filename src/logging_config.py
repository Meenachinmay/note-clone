import logging
from .config import config


def _to_level(level_value):
    if isinstance(level_value, int):
        return level_value
    if isinstance(level_value, str):
        return getattr(logging, level_value.upper(), logging.INFO)
    return logging.INFO


def setup_logging():
    """Configure production-grade logging once for the whole app.
    - Uses level/format from YAML config
    - Resets root handlers to avoid duplicates in reloads
    - Integrates uvicorn loggers to use the same formatting
    """
    level = _to_level(config['logging']['level'])
    log_format = config['logging']['format']

    root = logging.getLogger()
    root.setLevel(level)

    # Clear existing handlers to avoid duplicates (e.g., in reloads)
    for h in list(root.handlers):
        root.removeHandler(h)

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(log_format))
    root.addHandler(handler)

    # Make uvicorn loggers consistent
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers = []
        lg.propagate = True
        lg.setLevel(level)

    return logging.getLogger("app")


# Initialize on import
logger = setup_logging()
