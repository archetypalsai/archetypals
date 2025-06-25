from fastapi.security import APIKeyHeader
from fastapi import Security, HTTPException
from starlette.status import HTTP_403_FORBIDDEN
from config.settings import settings

api_key_header = APIKeyHeader(name="X-API-KEY")

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.ANYTHINGLLM_API_KEY:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Could not validate API key"
        )
    return api_key