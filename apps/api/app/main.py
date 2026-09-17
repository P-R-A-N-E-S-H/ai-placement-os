import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.exceptions import AppException, app_exception_handler, generic_exception_handler
from app.core.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan events."""
    logger.info("Initializing %s in %s mode...", settings.PROJECT_NAME, settings.ENVIRONMENT)
    
    # In development with SQLite, automatically create all registered tables
    if "sqlite" in settings.DATABASE_URL:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("SQLite database schema initialized successfully.")

    yield

    logger.info("Shutting down %s...", settings.PROJECT_NAME)
    await engine.dispose()
    logger.info("Database engine connections closed.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Multi-Agent Autonomous Career Intelligence & Placement Platform API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)




@app.middleware("http")
async def request_logging_and_id_middleware(request: Request, call_next):
    """Middleware to inject request_id and measure request duration."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        logger.info(
            "%s %s - %s (took %.2fms) [req_id: %s]",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
            request_id,
        )
        return response
    except Exception as exc:
        process_time = (time.time() - start_time) * 1000
        logger.error(
            "%s %s failed (took %.2fms) [req_id: %s] Error: %s",
            request.method,
            request.url.path,
            process_time,
            request_id,
            str(exc),
        )
        raise exc


# Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "REQUEST_VALIDATION_ERROR",
                "message": "Invalid request parameters or payload",
                "details": exc.errors(),
                "request_id": request_id,
            },
        },
    )


app.add_exception_handler(Exception, generic_exception_handler)

# Mount API Routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to AI PlacementOS API",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health",
        "version": "0.1.0",
    }
