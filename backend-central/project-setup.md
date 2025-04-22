# Setup venv
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