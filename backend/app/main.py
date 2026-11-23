from fastapi import FastAPI

from app.api.jobs import router

app = FastAPI(title="Stem Player")
app.include_router(router)
