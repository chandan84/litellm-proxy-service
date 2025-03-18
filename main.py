# main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from litellm import proxy_server

# Load dynamic configuration first
from config.dynamic_config import dynamic_config
from middlewares.custom_headers import CustomHeadersMiddleware

# Initialize dynamic config before loading environment
dynamic_config.setup_environment()
load_dotenv()

app = FastAPI(title="CLINE Dynamic Proxy")

# Add custom middleware
app.add_middleware(CustomHeadersMiddleware)

# Security setup
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

async def validate_api_key(api_key: str = Security(api_key_header)):
    expected_token = f"Bearer {os.getenv('PROXY_ACCESS_TOKEN')}"
    if api_key != expected_token:
        raise HTTPException(
            status_code=403,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Apply security to all routes
app.include_router(
    proxy_server.router,
    dependencies=[Depends(validate_api_key)]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("PROXY_HOST"),
        port=int(os.getenv("PROXY_PORT")),
        log_level="info"
    )
