from fastapi import FastAPI

from app.config import settings
from app.db import Base, engine
from app.routers.auth import router as auth_router

app = FastAPI(title=settings.app_name, debug=settings.debug)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router)
