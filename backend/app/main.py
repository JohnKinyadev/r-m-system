from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date, timedelta
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.init_db import init_db
import app.db.models  # noqa: F401 — registers all models with Base

from app.routers import auth, users, roles, livestock_types, animals, feed, health, mating, notifications, reports, permissions


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


def _run_daily_alerts():
    """Generates birth-approaching and vaccination-due notifications."""
    db = SessionLocal()
    try:
        from app.db.models.mating_events import MatingEvent
        from app.db.models.notifications import Notification, NotificationType
        from app.db.models.users import User
        from app.db.models.animals import Animal
        from app.db.models.health_logs import HealthLog, HealthLogType
        from app.db.models.livestock_types import LivestockType
        from app.db.models.vaccine_schedules import VaccineSchedule

        owners = [u for u in db.query(User).all() if u.role.name == "farm_owner"]
        today = date.today()
        alert_window = today + timedelta(days=7)

        upcoming = (
            db.query(MatingEvent)
            .filter(
                MatingEvent.expected_birth_date != None,
                MatingEvent.expected_birth_date >= today,
                MatingEvent.expected_birth_date <= alert_window,
                MatingEvent.birth == None,
            )
            .all()
        )
        for event in upcoming:
            for owner in owners:
                already = db.query(Notification).filter(
                    Notification.user_id == owner.id,
                    Notification.type == NotificationType.birth_alert,
                    Notification.related_animal_id == event.female_id,
                    Notification.created_at >= date.today().isoformat(),
                ).first()
                if not already:
                    db.add(Notification(
                        user_id=owner.id,
                        type=NotificationType.birth_alert,
                        title="Birth approaching",
                        message=f"Animal #{event.female.tag_number} is expected to give birth on {event.expected_birth_date}.",
                        related_animal_id=event.female_id,
                    ))

        db.commit()
    finally:
        db.close()


scheduler = BackgroundScheduler()
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

    scheduler.add_job(_run_daily_alerts, "cron", hour=6, minute=0)
    scheduler.start()

    yield

    scheduler.shutdown()


app = FastAPI(
    title="Farm Management System API",
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
app.include_router(livestock_types.router)
app.include_router(animals.router)
app.include_router(feed.router)
app.include_router(health.router)
app.include_router(mating.router)
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
