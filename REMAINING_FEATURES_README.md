# Remaining Features to Implement Later

> **Purpose:** Single reference for features that are **partial/incomplete** or **not yet done**. Use this when you implement them later.  
> **Last updated:** February 2025

---

## 1. Partially Done / Incomplete

### 1.1 Multi-tenant / Colleges (Phase 3)

**Done already:** Tables (`colleges`, `collegeid` on users/projects), college CRUD service + routes, AdminColleges.vue.

**To implement later:**

- [ ] **College-scoped queries**  
  In `user_management_service`, `project_service`, and any admin list/create/update:  
  - Get current user’s `collegeid` (and role).  
  - If role is **not** `super_admin`, filter all list/create/update by `collegeid` for `users` and `projects`.
- [ ] **Default college migration**  
  - Create one default college in DB.  
  - Set `collegeid` on all existing users and projects to that college.
- [ ] **Use `super_admin` and `clgadmin`**  
  - `super_admin`: platform-wide, no college filter.  
  - `clgadmin`: only their college’s data.  
  - Add role checks in dependencies and UI where needed.

---

### 1.2 Role Permissions (Phase 3)

**Done already:** Table `role_permissions`, service with `has_permission(role, resource, action)`, admin routes, AdminPermissions.vue.

**To implement later:**

- [ ] **Enforce permissions on routes**  
  - In `api/dependencies.py` add something like `require_permission(resource, action)` that:  
    - Gets current user role from JWT.  
    - Calls `has_permission(role, resource, action)`.  
    - Raises 403 if false.
- [ ] **Replace or combine with `require_role()`**  
  - For admin-only areas, either keep `require_role(["admin"])` or switch to `require_permission("users", "read")` etc. so the permission table actually controls access.

---

### 1.3 Chat – Realtime (Phase 3)

**Done already:** Tables `conversations`, `messages`, REST APIs, ChatView.vue (list conversations, send/receive messages).

**To implement later:**

- [ ] **Realtime updates**  
  - Use **Supabase Realtime** (or WebSocket) to subscribe to new messages for the current conversation.  
  - On new message, append to UI without refresh.  
  - Optional: unread badge / sound.

---

### 1.4 Soft Delete (Tech 6.4)

**Done already:** Columns `deleted_at` on `users`, `projects`, `modules`, `tasks` (migration 003).

**To implement later:**

- [ ] **Filter reads**  
  In all services that read from these tables, add `.is_("deleted_at", "null")` (or equivalent) so soft-deleted rows are never returned.
- [ ] **Use soft delete on “delete”**  
  - On user/project/module/task delete:  
    - `UPDATE` set `deleted_at = NOW()` instead of hard delete (where you want soft delete).  
  - Keep hard delete only where you explicitly need it (e.g. GDPR).

---

### 1.5 Comments UI in Task Detail (Phase 2)

**Done already:** Task comment APIs (list/add/delete for mentor and student), ChatView exists.

**To implement later:**

- [ ] **MentorTasks.vue**  
  - In the task/assignment detail or list row: add a “Comments” section that:  
    - Calls `commentsApi.list(assignmentId)`.  
    - Shows list of comments (user, text, time).  
    - Has input + button to call `commentsApi.add(assignmentId, comment)`.  
    - Optionally allow delete for own comments.
- [ ] **StudentMyTasks.vue**  
  - Same: comments section per assignment using `studentCommentsApi`.

---

## 2. Not Done at All

### 2.1 Testing (Tech 6.2)

- [ ] **Backend:** pytest for auth, roles, permissions; use TestClient for API tests; optional DB fixtures (Supabase or test DB).
- [ ] **Frontend:** Vitest + Vue Test Utils for components; basic smoke tests.
- [ ] **API contract:** pytest with TestClient; optional OpenAPI snapshot tests.

---

### 2.2 Structured JSON Logging (Tech 6.3)

- [ ] **JSON format**  
  - Configure logging so each log line is JSON (e.g. `{"request_id":"...", "level":"INFO", "message":"..."}`).
- [ ] **Levels**  
  - Use ERROR for auth failures, file upload errors, etc.  
  - Keep request_id in every log line (already set in middleware).

---

### 2.3 Error Tracking – Sentry (Tech 6.3)

- [ ] **Optional:** Integrate Sentry (or similar) for backend and/or frontend.  
- [ ] Capture unhandled exceptions and failed requests; link to request_id if possible.

---

### 2.4 Background Jobs (Tech 6.4)

- [ ] **Decouple email/notifications from request**  
  - Use Celery, ARQ, or similar to:  
    - Send emails (OTP, password reset, task assigned, etc.) via a task queue.  
    - Send in-app notifications via queue.  
  - Optionally: run “deadline approaching” checks on a schedule (e.g. cron) instead of only on login.

---

## 3. Quick Checklist

| # | Item | Area |
|---|------|------|
| 1 | College-scoped queries + default college + super_admin/clgadmin | Backend + optional UI |
| 2 | require_permission() in dependencies and use on routes | Backend |
| 3 | Chat realtime (Supabase Realtime or WebSocket) | Backend + Frontend |
| 4 | Soft delete: filter reads + set deleted_at on delete | Backend |
| 5 | Comments section in MentorTasks + StudentMyTasks | Frontend |
| 6 | pytest + Vitest + API tests | Backend + Frontend |
| 7 | JSON logging + ERROR levels | Backend |
| 8 | Sentry (optional) | Backend / Frontend |
| 9 | Background jobs (Celery/ARQ) for email + notifications | Backend |

---

When you implement a feature, tick the checkbox in this file and add a short note (e.g. “Done in branch x” or “Done 2025-03”) if you like.
