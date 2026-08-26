from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.init_db import init_db
import app.db.models  # noqa: F401 — registers all models with Base

from app.routers import (
    auth,
    expenses,
    ledger,
    maintenance,
    notifications,
    payments,
    permissions,
    properties,
    reports,
    roles,
    tenancies,
    tenants,
    units,
    users,
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

    yield


app = FastAPI(
    title="Rental Management System API",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(SlowAPIMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(roles.router)
app.include_router(users.router)
app.include_router(permissions.router)
app.include_router(properties.router)
app.include_router(units.router)
app.include_router(tenants.router)
app.include_router(tenancies.router)
app.include_router(ledger.router)
app.include_router(payments.router)
app.include_router(maintenance.router)
app.include_router(expenses.router)
app.include_router(notifications.router)
app.include_router(reports.router)


@app.get("/api/health-check")
def health_check():
    return {"status": "ok"}


@app.get("/.well-known/assetlinks.json")
def asset_links():
    """Digital Asset Links for Play Store TWA verification."""
    return JSONResponse([{
        "relation": ["delegate_permission/common.handle_all_urls"],
        "target": {
            "namespace": "android_app",
            "package_name": settings.ANDROID_PACKAGE_NAME,
            "sha256_cert_fingerprints": [settings.ANDROID_SHA256_CERT],
        }
    }])
