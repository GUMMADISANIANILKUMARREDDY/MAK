import logging
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from config.settings import settings

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class RequestIdAndLogMiddleware(BaseHTTPMiddleware):
    """Add X-Request-ID to request state and response; log request and response status."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            '{"request_id": "%s", "method": "%s", "path": "%s", "status": %s}',
            request_id, request.method, request.url.path, response.status_code,
        )
        return response
from api.routes.auth import router as auth_router
from api.routes.admin_users import router as admin_users_router
from api.routes.admin_students import router as admin_students_router
from api.routes.admin_projects import router as admin_projects_router
from api.routes.admin_activity import router as admin_activity_router
from api.routes.manager_modules import router as manager_modules_router
from api.routes.mentor_tasks import router as mentor_tasks_router
from api.routes.student_tasks import router as student_tasks_router
from api.routes.notifications import router as notifications_router
from api.routes.dashboard import router as dashboard_router
from api.routes.cron import router as cron_router
from api.routes.export_routes import router as export_router
from api.routes.admin_colleges import router as admin_colleges_router
from api.routes.admin_permissions import router as admin_permissions_router
from api.routes.chat import router as chat_router
from api.routes.push import router as push_router
from api.routes.reports import router as reports_router

app = FastAPI(title="InternHub API", version="1.0.0")


@app.get("/health")
def health():
    """Readiness/health check for load balancers and monitoring."""
    return {"status": "ok", "service": "InternHub API"}


app.add_middleware(RequestIdAndLogMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_users_router)
app.include_router(admin_students_router)
app.include_router(admin_projects_router)
app.include_router(admin_activity_router)
app.include_router(manager_modules_router)
app.include_router(mentor_tasks_router)
app.include_router(student_tasks_router)
app.include_router(notifications_router)
app.include_router(dashboard_router)
app.include_router(cron_router)
app.include_router(export_router)
app.include_router(admin_colleges_router)
app.include_router(admin_permissions_router)
app.include_router(chat_router)
app.include_router(push_router)
app.include_router(reports_router)


