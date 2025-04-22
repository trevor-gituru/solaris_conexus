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
# Postgressql
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
```
- Then exit:
```
\q

$ exit
```
- Add the database url to .env
# Auth
- Create the `auth` package
    + Create the `models.py` hold classes
    + Crete the `routes.py` to hanlde routing
## Setup registration
- Create `RegisterRequest` class to handle reg form data and validate it:
    + Install `pydantic[email]` dependecy handle email validation
- Create `hash_passwd` utils function:
    + Use `passlib[bcrypt]` dependecy to hash
- Create `register_user` async fn in routes:
    + Post route `/register`
    + Takes reg form data