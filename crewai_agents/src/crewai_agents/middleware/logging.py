import time
import logging
from fastapi import Request
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        logger.info(
            f"Request: {request.method} {request.url} "
            f"Completed in {process_time:.4f}s "
            f"Status: {response.status_code}"
        )
        
        return response