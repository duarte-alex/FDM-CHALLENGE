from fastapi import FastAPI
from .api.routes import router
from .database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Steel Production Forecast API",
    version="1.0.0",
    contact={
        "name": "GitHub Repository",
        "url": "https://github.com/duarte-alex/FDM-CHALLENGE.git",
    },
)
app.include_router(router)
