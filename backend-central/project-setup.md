# Setup venv and simple FastApi
- Install virtual enviroment:
```$ sudo apt install python3-venv```
- Setup virtual enviroment:
```$ python3 -m venv venv```
- Activate it:, to deactivate
```$ source venv/bin/activate```
```$ deactivate```
- Install dependency
```$ pip install fastapi uvicorn python-dotenv```
- Setup the `.env` file to hold frontend url
- Setup demo `main.py`:
    + Fetch backend url
    + Create FastApi and allow cors
    + When script is main run as server in port 8000
# Postgressql setup
- Install it & start it: 
```
$ sudo apt install postgresql postgresql-contrib
$ sudo systemctl start postgresql
$ sudo systemctl enable postgresql
$ sudo -i -u postgres
$ psql
```
- Create user & db `solaris`:
```
CREATE DATABASE solaris;
CREATE USER solaris_user WITH PASSWORD 'your_secure_password';
ALTER ROLE solaris_user SET client_encoding TO 'utf8';
ALTER ROLE solaris_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE solaris_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE solaris TO solaris_user;

ALTER USER postgres PASSWORD 'razor8617';
```
- Then exit:
```
\q

$ exit
```
- Add the database url to .env
- Edit 
```
$ sudo nano /etc/postgresql/<version>/main/pg_hba.conf
local   all             postgres                                peer
``
    + Change `peer` to `md5`
    + ```sudo service postgresql restart```
    

- Install `sqlalchemy psycopg2-binary alembic` dependencies to handle db
- Intialize alembic to manage migrations:
```$ alembic init alembic
```
- In the `alembic/env.py`:
    + Change the `config` object to get database url from `.env`
    + Load the `Base` & `models` form the database package
- Create a snapshot & push changes via:
```
$ alembic revision --autogenerate -m "Initial"
& alembic upgrade head
```

# Auth
- Create the `auth` package
    + Create the `models.py` hold classes
    + Crete the `routes.py` to hanlde routing
## Setup registration
- Create `RegisterRequest` class to handle reg form data and validate it:
    + Install `pydantic[email]` dependecy handle email validation
- Create `hash_passwd` utils function:
    + Use `passlib[bcrypt]` dependecy to hash
- Create the `User` model in `database`  package with same fields as `RegForm`
- Create `register_user` async fn in routes:
    + Post route `/register`
    + Takes reg form data

## Register User Feature

**Commit Summary:**  
Added user registration functionality including database model, user creation logic, and password hashing.

**Details:**

- **User Model** (`db/models.py`)  
  Created a `User` model with fields: `id`, `username`, `email`, and `hashed_password`. Applied constraints for uniqueness and non-nullability.

- **Password Hashing** (`auth/utils.py`)  
  Added a `hash_password()` function using `bcrypt` to securely hash passwords before storing them in the database.

- **User Creation Method** (`db/crud.py` or `db/utils.py`)  
  Defined `create_user(db, request)` to create and save new users using the Pydantic `RegisterRequest` model.

- **Registration Endpoint** (`auth/routes.py`)  
  Created a `/register` route that:
  - Validates username/email uniqueness
  - Hashes the password
  - Saves the user to the database
  - Returns a success message to the frontend

- **Tested Registration**  
  Tested using `curl` to ensure successful registration and duplicate-checking.
### JWT-Based Login Functionality

- Developed `LoginRequest` and `LoginResponse` models to define structure for login input and response.
- Created `/login` route to authenticate users using email and password.
- Added utility functions `create_token` and `decode_token` using `python-jose` to manage JWT tokens.
- Passwords are securely verified using `passlib.hash.bcrypt`.
- Implemented `/test` route that extracts and decodes JWT tokens from the `Authorization` header to validate user authentication.
- Installed required libraries: `passlib`, `bcrypt`, `python-jose`.


# docker
```
sudo apt update
sudo apt install ca-certificates curl gnupg lsb-release -y

sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io -y
sudo service docker start
sudo docker pull shardlabs/starknet-devnet-rs
echo "alias starknet-devnet='docker run --network host shardlabs/starknet-devnet-rs'" >> ~/.bashrc
source ~/.bashrc
```

# Hubs
- `Hub` table
- `routes` with `hubs`  prefix
- `create` route new Hub
- `get` route fetch HUb based on name & devices created under its name

