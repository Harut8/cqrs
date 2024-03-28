import asyncio
from contextlib import asynccontextmanager

from celery import Task

from app.helpers.celery_app import celery_app
from app.helpers.db import DB_HELPER
from app.helpers.exceptions import PgVectorError
from app.helpers.s3 import s3_aws
from app.helpers.vectorestore import vectorstore_pg


class BaseTask(Task):
    max_retries = 1
    default_retry_delay = 10


async def task():
    async with asynccontextmanager(DB_HELPER.session_dependency)() as db:
        ...


@celery_app.task(bind=True, base=BaseTask, name="file_to_vector")
def celery_task(
):
    try:
        loop = asyncio.get_event_loop()
    except Exception:
        loop = asyncio.new_event_loop()
    loop.run_until_complete(task())
