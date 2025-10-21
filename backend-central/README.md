# Central Backend

This directory contains the Central Backend service for the Solaris Conexus project. This FastAPI application serves as the main API for the entire system, handling business logic, data persistence, and communication with the Starknet blockchain.

## Overview

The primary responsibilities of the Central Backend are:
-   **API Endpoints:** Providing a comprehensive REST API for the frontend dashboard and the estate backends.
-   **User & Hub Management:** Handling user authentication, profiles, and the registration of energy hubs.
-   **Blockchain Interaction:** Connecting to the Starknet network to manage the Solaris Conexus Token (SCT), including minting, transfers, and trade requests.
-   **Data Persistence:** Managing all application data using a PostgreSQL database with SQLAlchemy ORM.

## Tech Stack

-   **Framework:** FastAPI
-   **Database:** PostgreSQL with SQLAlchemy ORM and Alembic for migrations.
-   **Authentication:** JWT (JSON Web Tokens)
-   **Blockchain:** Starknet.py for interacting with the Cairo smart contract.
-   **Async:** Uvicorn for serving the application.

## Project Structure

```
src/
├── auth/           # Authentication routes, requests, and responses
├── db/             # Database setup, models, and session management
├── hubs/           # API routes and logic for managing energy hubs
├── resident/       # API routes and logic for residents
├── schemas/        # Pydantic schemas for data validation
├── tests/          # Unit and integration tests
├── utils/          # Utility modules (Starknet, MQTT, email, etc.)
├── config.py       # Application configuration and environment variables
└── main.py         # Main FastAPI application entry point
```

## Getting Started

### Prerequisites

-   Python 3.11+
-   PostgreSQL database

### Installation

1.  Navigate to the `backend-central` directory:
    ```bash
    cd backend-central
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

Create a `.env` file in the `backend-central` directory and add the necessary environment variables (e.g., database URL, JWT secret, Starknet private key). Refer to `src/config.py` for the required variables.

### Database Migrations

Run the following command to apply the latest database migrations:

```bash
alembic upgrade head
```

### Running the Application

```bash
python3 -m src.main
```
