# InternHub / MAK — Features Implementation Roadmap

> **Purpose:** Single reference document for implementing all product gaps, features, and engineering improvements.  
> **Status:** Planning only — code development pending your approval.  
> **Last updated:** February 2025

---

## 1. Current Stack Summary (MVP+)

### What You Already Have ✅

| Area | Status |
|------|--------|
| **Auth** | Full flow: OTP, forgot/reset password, refresh tokens, roles (admin, manager, mentor, student, clgadmin) |
| **Admin CRUD** | Users, Students, Projects with assign-manager flow |
| **Manager → Modules** | Create/update/delete modules, assign mentors |
| **Mentor → Teams + Tasks** | Create teams, add students, create/assign tasks, bulk assign |
| **Student → Tasks** | View tasks, update status (assigned → in_progress → review), submit with file attachment |
| **Role-based UI** | Vue Dashboard with sidebar by role, lazy-loaded sections |
| **Infra** | File upload (Supabase Storage), email (SMTP), JWT, CORS, health check |

### Project Structure (Student Backend)

```
student/
├── app.py                    # FastAPI app, routes registration
├── config/
│   ├── settings.py           # Env vars, JWT, SMTP, CORS, storage bucket
│   └── supabase_client.py    # Supabase client
├── api/
│   ├── dependencies.py       # require_role(), get_current_user
│   └── routes/
│       ├── auth.py
│       ├── admin_users.py
│       ├── admin_students.py
│       ├── admin_projects.py
│       ├── manager_modules.py
│       ├── mentor_tasks.py
│       └── student_tasks.py
├── services/
│   ├── auth_service.py
│   ├── email_service.py      # OTP, password reset emails
│   ├── task_service.py       # Tasks, assignments, submissions, file upload
│   ├── module_service.py
│   ├── team_service.py
│   ├── project_service.py
│   ├── user_management_service.py
│   └── student_management_service.py
├── schemas/
│   ├── user.py
│   └── project.py            # TaskCreateRequest, TaskSubmissionRequest, etc.
├── utils/
│   └── email_templates.py
├── db/                       # SQL schemas (Supabase)
│   ├── users_table.sql
│   ├── students_table.sql
│   ├── pending_registrations_table.sql
│   ├── project_management_tables.sql
│   └── migration_to_varchar_userid.sql
└── migrations/
    └── 001_auth_and_submissions.sql   # refresh_tokens, password_reset_otps, submission_file_url
```

### Existing DB Tables (Supabase)

- `users` — userid, username, email, password, role, active  
- `students` — userid FK, college, etc.  
- `pending_registrations` — OTP flow  
- `projects`, `project_assignments`  
- `modules`, `module_assignments`  
- `teams`, `team_members`  
- `tasks`, `task_assignments` (with `submission_file_url`, `notes`)  
- `refresh_tokens`, `password_reset_otps`

---

## 2. Product Gaps & Missing Features

| # | Feature | Description | Current State |
|---|---------|-------------|---------------|
| 1 | **Notifications** | In-app + email alerts for assignments, status changes, deadlines, reviews | None |
| 2 | **Dashboard analytics** | Role-based stats (admin, manager, mentor, student) | Dashboards are navigation only |
| 3 | **Task review & grading** | Mentor approve/reject, feedback, score, status flow | Student submits → no mentor review flow |
| 4 | **File management** | Mentor download, review file upload, versioning, validation | Basic upload only |
| 5 | **Global search & filters** | Search across entities, filters by date/status/priority, sort | Basic lists only |
| 6 | **Multi-tenant / colleges** | colleges table, college-scoped data | Not implemented |

---

## 3. Phase 1 — Must-Have Polish

### 3.1 Notifications System (Very Important)

**Scope:** In-app notifications + email triggers.

#### Database

- New table: `notifications`
  - `id`, `userid` (recipient), `type`, `title`, `message`, `link`, `read`, `created_at`
  - Types: `task_assigned`, `task_status_changed`, `deadline_approaching`, `task_reviewed`, `student_added_to_team`, `mentor_assigned`
- Index on `(userid, read)`

#### Backend (student/)

- New service: `services/notification_service.py`
  - `create_notification(userid, type, title, message, link)`
  - `get_my_notifications(userid, unread_only, limit)`
  - `mark_as_read(notification_id)` / `mark_all_read(userid)`
- New routes: `api/routes/notifications.py`
  - `GET /notifications` — get my notifications
  - `PUT /notifications/{id}/read` — mark one
  - `PUT /notifications/read-all` — mark all
- Extend `email_service.py` with templates for:
  - Task assigned, task status changed, deadline approaching, task reviewed/rejected, student added, mentor assigned
- Trigger notifications in:
  - `task_service.assign_task_to_student`, `assign_task_bulk`
  - `task_service.update_task_assignment_status`, `submit_task`
  - `team_service.add_student_to_team`
  - `module_service` (mentor assignment)
  - Background job or cron for deadline_approaching (or on login)

#### Frontend (frontend/)

- Add `notificationsApi` in `api.js` (get, mark read)
- Add `NotificationBell.vue` in header/sidebar (dropdown or page)
- Dashboard shows notification count; optional toast on new events (if realtime added later)

---

### 3.2 Dashboard Analytics / Summaries

**Scope:** Role-based stats cards on dashboard Overview.

#### Backend (student/)

- New routes: `api/routes/dashboard.py`
  - `GET /dashboard/admin-stats` — total users, students, projects; active vs inactive
  - `GET /dashboard/manager-stats` — modules by status, tasks pending review
  - `GET /dashboard/mentor-stats` — tasks pending review, teams count
  - `GET /dashboard/student-stats` — tasks: pending / in_progress / review / done
- New service: `services/dashboard_service.py` — aggregate queries per role

#### Frontend (frontend/)

- Add `dashboardApi` in `api.js`
- Update `Dashboard.vue` Overview section: role-based stats cards (counts, small charts if desired)

---

### 3.3 Task Review & Feedback System

**Scope:** Mentor review flow: approve/reject, feedback, optional score.

#### Database

- Option A: `task_reviews` table
  - `id`, `assignment_id`, `reviewed_by`, `result` (approved/rejected), `feedback`, `score`, `created_at`
- Option B: Add columns to `task_assignments`
  - `review_result`, `review_feedback`, `review_score`, `reviewed_at`, `reviewed_by`

#### Backend (student/)

- Extend `task_assignments.status` flow: `submitted` → `under_review` → `approved` / `rejected`
- New schemas: `TaskReviewRequest` (result, feedback, score)
- `task_service.review_task(assignment_id, result, feedback, score)` — update assignment, create notification
- New routes in `mentor_tasks.py`:
  - `POST /mentor/tasks/assignments/{assignment_id}/review`

#### Frontend (frontend/)

- Mentor: review UI in task assignments list (approve/reject, feedback text, optional score)
- Student: show review result and feedback on task detail

---

### 3.4 Search & Filters

**Scope:** Search across entities, filters by date/status/priority, sorting.

#### Backend (student/)

- Extend existing list endpoints with query params:
  - `search` — text search (users, students, projects, tasks, modules)
  - `status`, `priority`, `date_from`, `date_to`
  - `sort` — e.g. `due_date`, `updated_at`, `priority`
  - `order` — asc/desc
- Use Supabase `.ilike()`, `.gte()`, `.lte()` for filters
- Add DB indexes where needed (e.g. `tasks.due_date`, `tasks.status`)

#### Frontend (frontend/)

- Add search input + filter dropdowns to:
  - AdminUsers, AdminStudents, AdminProjects
  - ManagerModules, MentorTasks, StudentMyTasks
- Use existing `params` in api calls; wire to filters

---

## 4. Phase 2 — Professional Features

### 4.1 Activity Logs / Audit Trail

- New table: `activity_logs` — `id`, `userid`, `action`, `entity_type`, `entity_id`, `payload`, `ip`, `created_at`
- Log on create/update/delete for users, projects, modules, tasks, assignments
- New routes: `GET /admin/activity-logs` (admin only), filter by entity/user/date
- New service: `services/activity_service.py`

---

### 4.2 Comment System on Tasks/Modules

- New table: `task_comments` — `id`, `assignment_id`, `userid`, `comment`, `created_at`
- Optional: `module_comments` if needed
- APIs: list, create, delete
- UI: comments section in task detail for mentor/student

---

### 4.3 File Management Improvements

- Mentor download: add `GET /mentor/tasks/assignments/{id}/submission` to return signed URL for `submission_file_url`
- Mentor review file: new column `review_file_url` on `task_assignments`; upload endpoint for mentor
- Versioning: `task_submission_versions` table — assignment_id, file_url, version, created_at
- Resubmission: allow student to submit again (new version) when status is `rejected`
- Validation: backend max size (e.g. 10MB), allowed types (pdf, docx, etc.); frontend same checks

---

### 4.4 Export to CSV

- New routes: `GET /admin/students/export`, `GET /admin/projects/export`, `GET /mentor/tasks/export`
- Use streaming response with CSV; role checks
- Frontend: Export button on list views

---

## 5. Phase 3 — Scale & SaaS

### 5.1 Multi-Tenant / Colleges

- New table: `colleges` — `collegeid`, `name`, `code`, `created_at`
- Add `collegeid` FK to `users`, `projects` (and optionally modules/tasks)
- New roles: `super_admin` (platform), `clgadmin` (college admin)
- All list/create/update queries filter by `collegeid` for non-super_admin
- Migration: assign existing data to a default college

---

### 5.2 Role Permissions UI

- New table: `role_permissions` — role, resource, action (create, read, update, delete)
- Admin UI to configure permissions per role
- `dependencies.py` checks permissions dynamically

---

### 5.3 In-App Chat (Mentor ↔ Student)

- New tables: `conversations`, `messages`
- Real-time via Supabase Realtime or WebSocket
- UI: chat widget or dedicated page

---

### 5.4 Reports (PDF / Excel)

- Use libraries: ReportLab / WeasyPrint (PDF), openpyxl (Excel)
- Reports: project summary, student progress, task completion
- Routes: `GET /admin/reports/project-summary`, etc.

---

## 6. Tech / Engineering Gaps

### 6.1 Security

| Item | Implementation |
|------|----------------|
| Rate limiting | Add `slowapi` or custom middleware for `/auth/login`, `/auth/otp`, `/auth/forgot-password` (e.g. 10/min) |
| Password strength | Pydantic validator: min length 8, uppercase, lowercase, number, special |
| Account lock | `failed_login_attempts`, `locked_until` on users; increment on wrong password, lock for 15 min after 5 fails |
| Refresh token rotation | On refresh: issue new refresh token, revoke old (delete from `refresh_tokens`) |

---

### 6.2 Testing

| Area | Approach |
|------|----------|
| Backend | pytest for auth, roles, permissions; fixtures for DB (Supabase client or test DB) |
| Frontend | Vitest + Vue Test Utils for components; basic smoke tests |
| API contract | pytest with `TestClient`; optional OpenAPI snapshot tests |

---

### 6.3 Logging & Monitoring

- Structured logs: JSON format; log level ERROR for auth failures, file upload issues
- Request ID: middleware to add `X-Request-ID`; include in log lines
- Optional: Sentry (or similar) for error tracking

---

### 6.4 DB & Performance

- Indexes: ensure `user_id`, `project_id`, `module_id`, `task_id`, `assignment_id` on FKs and frequent filters
- Soft delete: add `deleted_at` to users, projects, modules, tasks; filter `WHERE deleted_at IS NULL` in reads; `UPDATE` on delete
- Background jobs: Celery or ARQ for email sending, notification dispatch (decouple from request)

---

## 7. Implementation Checklist (Summary)

| Phase | Feature | DB | Backend | Frontend |
|-------|---------|----|---------|----------|
| 1 | Notifications | `notifications` | service, routes, email triggers | Bell, dropdown |
| 1 | Dashboard stats | — | dashboard routes, service | Stats cards |
| 1 | Task review | `task_reviews` or cols on `task_assignments` | review API | Mentor review UI |
| 1 | Search & filters | indexes | extend list APIs | Search + filters |
| 2 | Activity logs | `activity_logs` | service, routes | Admin logs view |
| 2 | Comments | `task_comments` | CRUD APIs | Comments UI |
| 2 | File improvements | `task_submission_versions`, cols | download, review upload | Download, resubmit |
| 2 | CSV export | — | export routes | Export buttons |
| 3 | Multi-tenant | `colleges` | college-scoped queries | — |
| 3 | Permissions UI | `role_permissions` | permission checks | Admin permissions |
| 3 | Chat | `conversations`, `messages` | chat APIs + realtime | Chat UI |
| 3 | Reports | — | report routes | Report downloads |

---

## 8. Next Steps

1. **Review this roadmap** — confirm scope and priorities.  
2. **Approve for code development** — specify which phase(s) to start with.  
3. **Implementation order** — Phase 1 is recommended first (notifications, stats, task review, filters).

---

*Document created for MAK/InternHub. Do not develop code until explicit approval.*
