from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import auth_router, request_router, users_router, notification_router

app = FastAPI(
    title="EcoRetiro API",
    description="Plataforma de gestión de retiro y reciclaje de residuos electrónicos",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:5500"],
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

@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok", "project": "EcoRetiro API"}