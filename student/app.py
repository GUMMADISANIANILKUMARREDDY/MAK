from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.auth import router as auth_router
from api.routes.admin_users import router as admin_users_router
from api.routes.admin_students import router as admin_students_router
from api.routes.admin_projects import router as admin_projects_router
from api.routes.manager_modules import router as manager_modules_router
from api.routes.mentor_tasks import router as mentor_tasks_router
from api.routes.student_tasks import router as student_tasks_router

app = FastAPI(title="InternHub API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_users_router)
app.include_router(admin_students_router)
app.include_router(admin_projects_router)
app.include_router(manager_modules_router)
app.include_router(mentor_tasks_router)
app.include_router(student_tasks_router)


