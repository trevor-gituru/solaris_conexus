# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings

from src.auth.routes import router as auth_router
from src.resident.routes import router as resident_router
from src.hubs.routes import router as hub_router

app = FastAPI()

# Apply CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(resident_router, prefix="/residents", tags=["Residents"])
app.include_router(hub_router, prefix="/hubs")

# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)

