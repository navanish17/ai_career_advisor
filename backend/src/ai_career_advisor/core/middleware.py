import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ai_career_advisor.core.logger import logger


def add_middlewares(app: FastAPI):
    
    app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",      
        "http://127.0.0.1:8080"  
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
 )
    

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)
        duration = (time.time() - start_time) * 1000  # ms

        logger.info(
            f"{request.method} {request.url.path} "
            f"→ {response.status_code} ({duration:.2f} ms)"
        )
        return response

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled error at {request.url}: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}
        )
    

