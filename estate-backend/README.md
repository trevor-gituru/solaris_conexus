# Estate Backend

This directory contains the Estate Backend service for the Solaris Conexus project. This Python application acts as a local gateway, bridging communication between the on-site Arduino IoT devices and the central backend system.

## Overview

The primary responsibilities of the Estate Backend are:
-   **IoT Communication:** Subscribing to and processing data from Arduino devices via the MQTT protocol.
-   **Data Relay:** Forwarding energy consumption/production data to the central backend.
-   **Device Control:** Receiving commands from the central backend and relaying them to the appropriate Arduino device.
-   **Local Caching:** Storing local data and state using a database.

## Tech Stack

-   **Language:** Python
-   **Communication:** Paho-MQTT for IoT device communication, HTTP client (e.g., `requests` or `httpx`) for central API communication.
-   **Database:** PostgreSQL with SQLAlchemy ORM and Alembic for migrations.

## Project Structure

```
src/
├── central_api/    # Client for communicating with the central backend API
├── db/             # Database setup, models, and session management
├── homes/          # Logic for interfacing with Arduino devices
├── mqtt/           # MQTT client for IoT communication
├── starknet/       # Functions for interacting with the Starknet blockchain
├── tests/          # Unit and integration tests
├── utils/          # Utility functions
├── config.py       # Application configuration and environment variables
└── main.py         # Main application entry point
```

## Getting Started

### Prerequisites

-   Python 3.11+
-   PostgreSQL database
-   An MQTT broker (e.g., Mosquitto)

### Installation

1.  Navigate to the `estate-backend` directory:
    ```bash
    cd estate-backend
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Environment Variables

Create a `.env` file in the `estate-backend` directory and add the necessary environment variables (e.g., database URL, MQTT broker address, central API URL). Refer to `src/config.py` for the required variables.

### Database Migrations

Run the following command to apply the latest database migrations:

```bash
alembic upgrade head
```

### Running the Application

```bash
python -m src.main
```
