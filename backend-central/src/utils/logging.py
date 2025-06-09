# /src/utils/logging.py
import logging

logger = logging.getLogger("solaris_conexus")
logger.setLevel(logging.INFO)

# Avoid adding multiple handlers in reloads (e.g., with uvicorn)
if not logger.handlers:
    # Console handler with formatting
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

