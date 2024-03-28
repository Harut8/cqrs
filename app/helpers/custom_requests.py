import json
from functools import wraps
from typing import Any, Callable

import httpx

from app.helpers.exceptions import RequestError, ServiceUnavailableException
from app.settings import APP_SETTINGS

ORGANIZATION_URL = APP_SETTINGS.API_CALL.ORGANIZATION


def request_exception_handler(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            raise RequestError(
                status_code=e.response.status_code,
                message="Something went wrong. Problem likes network issue or server error.",
            ) from e
        except httpx.ConnectError as e:
            raise ServiceUnavailableException() from e

    return wrapper


def run_request(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        global ORGANIZATION_URL
        async with httpx.AsyncClient() as client:
            kwargs["client"] = client
            kwargs["timeout"] = 5 * 60
            base_url = kwargs.get("base_url")
            ORGANIZATION_URL = ORGANIZATION_URL if not base_url else base_url
            response = await func(*args, **kwargs)
            response.raise_for_status()
            try:
                return response.json()
            except json.JSONDecodeError:
                pass
            return response.status_code in [200, 201, 204]

    return wrapper


@request_exception_handler
@run_request
async def create_get_request(url, client, **kwargs):
    return await client.get(f"{ORGANIZATION_URL}{url}", **kwargs)


@request_exception_handler
@run_request
async def create_post_request(url, client, data=None, **kwargs):
    return (
        await client.post(f"{ORGANIZATION_URL}{url}", data=json.dumps(data), **kwargs)
        if data
        else await client.post(f"{ORGANIZATION_URL}{url}", **kwargs)
    )


@request_exception_handler
@run_request
async def create_delete_request(url, client, **kwargs):
    return await client.delete(f"{ORGANIZATION_URL}{url}", **kwargs)
