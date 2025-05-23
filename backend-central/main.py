from auth.routes import router as auth_router
from dashboard.routes import router as dashboard_router
from hubs.routes import router as hub_router
# from dashboard.eth import router as eth_router
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Get the CORS origins from the environment variable
allowed_origins = os.getenv("CORS_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Adjust if using different host
    allow_credentials=True,
    allow_methods=["*"],  # Accept all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Accept all headers
)


app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(hub_router, prefix="/hubs")   # all hub_router routes start with /hubs
# app.include_router(eth_router, prefix="/eth", tags=["power-token"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

