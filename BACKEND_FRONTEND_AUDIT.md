# Backend & Frontend API Audit Report

**Date:** February 2025  
**Scope:** All backend routes (student/) and frontend API usage (frontend/src).  
**Status:** Checked and one bug fixed; one minor improvement applied.

---

## 1. Summary

| Area | Status | Notes |
|------|--------|--------|
| Backend route registration | ✅ OK | All 8 routers included in app.py |
| Auth APIs | ✅ OK | Login, register, verify, refresh, me, forgot/reset, change-password match frontend |
| Admin Users | ✅ OK | List, get, create, update, delete, bulk create/delete; params match |
| Admin Students | ✅ OK | Same pattern; bulk-delete uses AdminBulkDeleteRequest (userids) |
| Admin Projects | ✅ OK | List with search/filters/sort; CRUD + assign-manager, managers |
| Manager Modules | ✅ OK | my-projects, project modules (with params), CRUD, assign-mentor |
| Mentor Tasks & Teams | ✅ OK | Teams CRUD, module tasks with params, task CRUD, assign, bulk-assign, review |
| Student Tasks | ✅ OK | my-tasks (params), get task, update-status, submit (file) |
| Notifications | ✅ Fixed | Route order: PUT /read-all now before PUT /{id}/read (was wrong) |
| Dashboard | ✅ OK | admin/manager/mentor/student-stats match frontend |
| Frontend logout | ✅ Improved | Dashboard logout now also clears refresh_token |

---

## 2. Backend Routes (Full List)

Base URL: `http://localhost:8001` (or `VITE_API_BASE_URL`)

### Auth (`/auth`)
| Method | Path | Frontend usage |
|--------|------|----------------|
| POST | /auth/register | authService.register |
| POST | /auth/verify-email | authService.verifyEmail |
| POST | /auth/login | authService.login |
| POST | /auth/resend-otp | authService.resendOtp |
| POST | /auth/change-password | authService.changePassword |
| POST | /auth/forgot-password | authService.forgotPassword |
| POST | /auth/reset-password | authService.resetPassword |
| POST | /auth/refresh | api interceptor (auto) |
| GET | /auth/me | authService.getMe, Dashboard fallback |

### Admin Users (`/admin/users`)
| Method | Path | Frontend usage |
|--------|------|----------------|
| GET | /admin/users/ | usersApi.list(params) |
| GET | /admin/users/role/{role} | (optional) |
| GET | /admin/users/{userid} | usersApi.getById |
| POST | /admin/users/single | usersApi.createSingle |
| POST | /admin/users/bulk | usersApi.createBulk |
| PUT | /admin/users/{userid} | usersApi.update |
| DELETE | /admin/users/{userid} | usersApi.delete |
| POST | /admin/users/bulk-delete | usersApi.bulkDelete |

### Admin Students (`/admin/students`)
| Method | Path | Frontend usage |
|--------|------|----------------|
| GET | /admin/students/ | studentsApi.list(params) |
| GET | /admin/students/{userid} | studentsApi.getById |
| POST | /admin/students/single | studentsApi.createSingle |
| POST | /admin/students/bulk | studentsApi.createBulk |
| PUT | /admin/students/{userid} | studentsApi.update |
| DELETE | /admin/students/{userid} | studentsApi.delete |
| POST | /admin/students/bulk-delete | studentsApi.bulkDelete |

### Admin Projects (`/admin/projects`)
| Method | Path | Frontend usage |
|--------|------|----------------|
| GET | /admin/projects/ | projectsApi.list(params) |
| GET | /admin/projects/{projectid} | projectsApi.getById |
| POST | /admin/projects/create | projectsApi.create |
| PUT | /admin/projects/{projectid} | projectsApi.update |
| DELETE | /admin/projects/{projectid} | projectsApi.delete |
| POST | /admin/projects/{projectid}/assign-manager | projectsApi.assignManager |
| GET | /admin/projects/{projectid}/managers | projectsApi.getManagers |

### Manager (`/manager`)
| Method | Path | Frontend usage |
|--------|------|----------------|
| GET | /manager/my-projects | managerApi.myProjects |
| GET | /manager/projects/{projectid}/modules | managerApi.getProjectModules(projectid, params) |
| GET | /manager/modules/{moduleid} | managerApi.getModule |
| POST | /manager/projects/{projectid}/modules/create | managerApi.createModule |
| PUT | /manager/modules/{moduleid} | managerApi.updateModule |
| DELETE | /manager/modules/{moduleid} | managerApi.deleteModule |
| POST | /manager/modules/{moduleid}/assign-mentor | managerApi.assignMentor |
| GET | /manager/modules/{moduleid}/mentors | managerApi.getModuleMentors |

### Mentor (`/mentor`)
| Method | Path | Frontend usage |
|--------|------|----------------|
| GET | /mentor/my-modules | mentorApi.myModules |
| POST | /mentor/teams/create | mentorApi.createTeam |
| GET | /mentor/teams | mentorApi.getTeams |
| POST | /mentor/teams/{teamid}/add-student | mentorApi.addStudentToTeam |
| GET | /mentor/teams/{teamid}/members | mentorApi.getTeamMembers |
| DELETE | /mentor/teams/{teamid}/remove-student/{student_userid} | mentorApi.removeStudentFromTeam |
| DELETE | /mentor/teams/{teamid} | mentorApi.deleteTeam |
| GET | /mentor/modules/{moduleid}/tasks | mentorApi.getModuleTasks(moduleid, params) |
| GET | /mentor/tasks/{taskid} | mentorApi.getTask |
| POST | /mentor/modules/{moduleid}/tasks/create | mentorApi.createTask |
| PUT | /mentor/tasks/{taskid} | mentorApi.updateTask |
| DELETE | /mentor/tasks/{taskid} | mentorApi.deleteTask |
| POST | /mentor/tasks/{taskid}/assign-student | mentorApi.assignStudent |
| POST | /mentor/tasks/{taskid}/bulk-assign | mentorApi.bulkAssign |
| GET | /mentor/tasks/{taskid}/assignments | mentorApi.getTaskAssignments |
| POST | /mentor/tasks/assignments/{assignment_id}/review | mentorApi.reviewAssignment |

### Student (`/student`)
| Method | Path | Frontend usage |
|--------|------|----------------|
| GET | /student/my-tasks | studentApi.myTasks(params) |
| GET | /student/tasks/{taskid} | studentApi.getTask |
| PUT | /student/tasks/{assignment_id}/update-status | studentApi.updateStatus (body: { status }) |
| POST | /student/tasks/{assignment_id}/submit | studentApi.submit (FormData: notes, file) |

### Notifications (`/notifications`)
| Method | Path | Frontend usage |
|--------|------|----------------|
| GET | /notifications | notificationsApi.list(params) |
| GET | /notifications/unread-count | notificationsApi.unreadCount |
| PUT | /notifications/read-all | notificationsApi.markAllRead |
| PUT | /notifications/{notification_id}/read | notificationsApi.markRead |

### Dashboard (`/dashboard`)
| Method | Path | Frontend usage |
|--------|------|----------------|
| GET | /dashboard/admin-stats | dashboardApi.getAdminStats |
| GET | /dashboard/manager-stats | dashboardApi.getManagerStats |
| GET | /dashboard/mentor-stats | dashboardApi.getMentorStats |
| GET | /dashboard/student-stats | dashboardApi.getStudentStats |

---

## 3. Fixes Applied

1. **Notifications route order (backend)**  
   `PUT /notifications/read-all` was defined after `PUT /notifications/{notification_id}/read`. FastAPI would treat "read-all" as a notification_id. **Fixed:** Moved `PUT /read-all` above `PUT /{notification_id}/read` in `student/api/routes/notifications.py`.

2. **Logout (frontend)**  
   Dashboard logout now also removes `refresh_token` from localStorage so a full logout is consistent. (`Dashboard.vue`)

---

## 4. Request/Response Consistency

- **Admin bulk delete:** Frontend sends `{ userids: string[] }`; backend expects `AdminBulkDeleteRequest(userids: List[str])`. ✅  
- **Student update status:** Frontend sends `{ status }`; backend expects `TaskStatusUpdateRequest(status: str)`. ✅  
- **Task review:** Frontend sends `{ result, feedback?, score? }`; backend expects `TaskReviewRequest`. ✅  
- **Login:** Backend returns `LoginResponse` with `user`; frontend stores `response.user` or falls back to getMe(). ✅  

---

## 5. Optional / Future Checks

- **Search input:** Backend uses `.or_("col.ilike.%q%")` with user-supplied `q`. If you allow special characters (e.g. `%`, `\`), consider sanitizing or parameterizing to avoid unexpected behavior.  
- **CORS:** Ensure `VITE_API_BASE_URL` (or backend `CORS_ORIGINS`) matches your frontend origin in production.  
- **DB migrations:** Run `001_auth_and_submissions.sql` and `002_phase1_notifications_and_review.sql` in Supabase so notifications and task review columns exist.

---

## 6. Conclusion

Backend and frontend are aligned. One backend bug (notifications route order) was fixed and one frontend improvement (logout clearing refresh_token) was applied. All listed APIs are wired correctly and request/response shapes match.
