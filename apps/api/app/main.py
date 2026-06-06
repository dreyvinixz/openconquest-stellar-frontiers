from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import health
from app.routers.rooms import router as rooms_router
from app.websocket import routes as websocket_routes

from contextlib import asynccontextmanager
from app.database import Base, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title='OpenConquest: Stellar Frontiers API',
    version='0.1.0',
    lifespan=lifespan
)

# Set up CORS
origins = [origin.strip() for origin in settings.cors_origins.split(',') if origin.strip()]
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(health.router, prefix='/api/v1')
app.include_router(rooms_router, prefix='/api/v1')
app.include_router(websocket_routes.router)
