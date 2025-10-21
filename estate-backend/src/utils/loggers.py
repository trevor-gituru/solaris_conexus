# src/utils/loggers.py

# /src/utils/logging.py

import logging
from colorlog import ColoredFormatter

def get_service_logger(service_name: str) -> logging.Logger:
    logger = logging.getLogger(f"estate_hub.{service_name}")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)

        formatter = ColoredFormatter(
            fmt=f"%(log_color)s%(asctime)s - %(levelname)s - [{service_name}] - %(message)s",
            log_colors={
                "DEBUG":    "cyan",
                "INFO":     "green",
                "WARNING":  "yellow",
                "ERROR":    "red",
                "CRITICAL": "bold_red",
            }
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

# Create loggers for each service
central_logger = get_service_logger("CentralAPIClient")
starknet_logger = get_service_logger("Starknet")
mqtt_logger = get_service_logger("MQTTService")
arduino_logger = get_service_logger("ArduinoService")
