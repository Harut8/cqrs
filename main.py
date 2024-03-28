import logging
import sys
from contextlib import asynccontextmanager

import uvloop
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.cors import CORSMiddleware

from app.helpers.db import DB_HELPER
from app.helpers.exceptions import NotFound, ServiceException, ValidationError
from app.helpers.rabbitmq import RMQ_Client, consumer
from app.helpers.response import Response
from app.api_v1.user_router.router import user_router

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))


@asynccontextmanager
async def lifespan(f_app: FastAPI):
    async with asynccontextmanager(DB_HELPER.scoped_session_dependency)() as _:
        print("DB Connected")
    await RMQ_Client.connect()
    print("RabbitMQ Connected")
    await consumer()
    print("RabbitMQ Consumer Connected")
    yield


app = FastAPI(
    lifespan=lifespan,
    docs_url="/swagger",
    openapi_url="/openapi.json",
)

app.include_router(user_router)
Instrumentator().instrument(app).expose(app)
origins: set = {
    "*",
    "http://localhost",
    "http://localhost:*",
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

uvloop.install()


@app.exception_handler(404)
async def not_found(request, exc):
    return NotFound(message="Resource not found").to_response()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return ValidationError().to_response()


@app.exception_handler(500)
async def server_error_handler(request, exc):
    return ServiceException().to_response()


@app.get("/health-check")
async def health_check():
    return Response(status_code=200, message="App is up and running!")

# TODO: Add API KEYS, PREFIX, DOCS, OPENAPI ENV, ROOT PATH, LOGGING
# TODO: ADD MODEL INDEXES FOR OPTIMIZATION
# TODO: ADD DATABASE INDEXES
