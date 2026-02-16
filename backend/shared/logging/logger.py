import logging
import sys
from pathlib import Path

def setup_logging(service_name: str, debug: bool = False) -> None:
    """
    Configure application-wide logging.
    Logs are written to STDOUT (Docker-friendly).
    """

    handlers = []

    console_handler = logging.StreamHandler(sys.stdout)
    handlers.append(console_handler)

    # Optional file logging in debug mode
    if debug:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(log_dir / f"{service_name}.log")
        handlers.append(file_handler)

    logging.basicConfig(
            level=logging.INFO,
            format=f"%(asctime)s | {service_name} | %(levelname)s | %(message)s",
            handlers=handlers,
    )
