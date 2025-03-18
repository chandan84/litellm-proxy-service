# main.py
from fastapi import FastAPI, Request, HTTPException
from litellm.proxy.proxy_server import app, save_worker_config, initialize
from litellm.proxy.hooks import proxy_logging_obj
from litellm import Router
import os
import uuid

# 1. Custom API Key Generator (Implement your logic here) ⚙️
def generate_dynamic_api_key() -> str:
    """
    REPLACE THIS WITH YOUR ACTUAL KEY GENERATION LOGIC
    Example implementation:
    - Key rotation based on time
    - JWT token generation
    - Secrets manager call
    """
    return "dynamic-azure-key-" + str(uuid.uuid4())

# 2. Custom Header Manager 🌐
def get_custom_gateway_headers(request: Request) -> dict:
    """Return headers needed for your custom API gateway"""
    return {
        "X-API-Gateway-Auth": os.getenv("GATEWAY_AUTH_SECRET"),
        "X-Client-ID": "vs-code-cline",
        "X-Request-ID": request.headers.get("X-Request-ID", str(uuid.uuid4()))
    }

# 3. Pre-Call Hook for Request Manipulation ⚡
async def azure_request_hook(data: dict, request: Request):
    # Override any incoming API key with our dynamic key
    data["api_key"] = generate_dynamic_api_key()
    
    # Merge existing headers with gateway requirements
    data["headers"] = {
        **data.get("headers", {}),
        **get_custom_gateway_headers(request)
    }
    
    # Force Azure-specific parameters
    data["api_base"] = os.getenv("AZURE_API_BASE")
    data["api_version"] = os.getenv("AZURE_API_VERSION")
    
    return data

# 4. Azure OpenAI Configuration 🔧
config = {
    "environment_variables": {
        "AZURE_API_BASE": os.getenv("AZURE_API_BASE"),
        "AZURE_API_VERSION": os.getenv("AZURE_API_VERSION")
    },
    "model_list": [{
        "model_name": "cline-azure-prod",
        "litellm_params": {
            "model": "azure/your-deployment-name",
            "api_base": "os.getenv('AZURE_API_BASE')",
            "api_version": "os.getenv('AZURE_API_VERSION')",
            "api_key": "os.getenv('AZURE_API_KEY')"  # Will be overridden
        }
    }]
}

# 5. Proxy Setup 🚀
app = FastAPI(title="CLINE Azure Proxy")

# Initialize LiteLLM with custom config
save_worker_config(config)
initialize(config=config, telemetry=False)

# Bypass LiteLLM auth and setup hooks
@app.on_event("startup")
async def setup_custom_flow():
    # Bypass authentication for CLINE extension
    from litellm.proxy.proxy_server import user_api_key_cache
    user_api_key_cache.set_cache({
        "cline-extension-key": {  # Hardcoded key from VS Code settings
            "api_key": "dummy", 
            "allowed_model_region": "azure"
        }
    })
    
    # Register our custom request hook
    proxy_logging_obj.pre_call_hooks = [azure_request_hook]

# 6. Request Validation Middleware 🔐
@app.middleware("http")
async def validate_request_format(request: Request, call_next):
    # Block non-CLINE requests
    if request.url.path == "/chat/completions":
        if request.headers.get("User-Agent") != "CLINE-VSCode":
            raise HTTPException(403, "Forbidden client")
    
    return await call_next(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
