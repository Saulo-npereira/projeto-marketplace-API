from fastapi import FastAPI

app = FastAPI()

from auth_routes import auth_router
from produtos_routes import produtos_router
app.include_router(auth_router)
app.include_router(produtos_router)