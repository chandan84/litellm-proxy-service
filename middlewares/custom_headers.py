# middlewares/custom_headers.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class CustomHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        
        # Add custom headers to response
        response.headers["X-Proxy-Service"] = "CLINE-LiteLLM-Proxy"
        response.headers["X-Model-Source"] = request.headers.get(
            "X-Model-Source", "default"
        )
        
        return response
