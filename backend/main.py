from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from backend.routers import (
    auth_router,
    request_router,
    users_router,
    notification_router,
    dashboard_router,
)


default_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]
origins_env = os.getenv("FRONTEND_ORIGINS", "")
allowed_origins = [
    o.strip() for o in origins_env.split(",") if o.strip()
] or default_origins

app = FastAPI(
    title="EcoRetiro API",
    description="Plataforma de gestión de retiro y reciclaje de residuos electrónicos",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router.router)
app.include_router(request_router.router)
app.include_router(request_router.track_router)
app.include_router(users_router.router)
app.include_router(notification_router.router)
app.include_router(dashboard_router.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok", "project": "EcoRetiro API"}
