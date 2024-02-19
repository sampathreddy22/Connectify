import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from connectify.database import database
from connectify.logging_conf import configure_logging
from connectify.routers.post import router as post_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    configure_logging()
    logger.info("Connecting to the database")
    await database.connect()
    logger.info("Connected to the database")
    yield
    logger.info("Disconnecting from the database")
    await database.disconnect()
    logger.info("Disconnected from the database")


app = FastAPI(lifespan=lifespan)
app.include_router(post_router, prefix="/api/v1")
