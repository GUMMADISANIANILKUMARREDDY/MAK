# GitHub configuration for CI/CD

Configure these in your **GitHub repo** so Actions run correctly.

---

## 1. Secrets (Actions)

**Path:** Repo → **Settings** → **Secrets and variables** → **Actions** → **Secrets**

| Secret | Used by | Required? | Notes |
|--------|---------|-----------|--------|
| `SUPABASE_URL` | Backend CI (tests) | Optional | Your Supabase project URL. If missing, CI uses a placeholder; tests that only use mocked auth still pass. |
| `SUPABASE_SERVICE_KEY` | Backend CI (tests) | Optional | Supabase service role key. Set if tests need real DB. |

**To add:** Click **New repository secret**, name e.g. `SUPABASE_URL`, paste the value.

---

## 2. Variables (optional)

**Path:** Repo → **Settings** → **Secrets and variables** → **Actions** → **Variables**

You can add **Variables** (non-sensitive) for things like:

- `NODE_VERSION` (e.g. `20`) – used in frontend CI if you reference it in the workflow.
- `PYTHON_VERSION` (e.g. `3.12`) – same for backend.

The current workflows hardcode these; you can switch to variables later if you want.

---

## 3. Branch protection (optional)

**Path:** Repo → **Settings** → **Branches** → **Add rule** (e.g. for `main`)

- **Require status checks before merging:** enable and select **Backend CI** and **Frontend CI** (or the jobs you care about).
- **Require branches to be up to date:** optional.

Then PRs to `main` must pass the selected checks.

---

## 4. Permissions

Workflows use default `GITHUB_TOKEN` permissions. No extra permissions are needed for:

- Checkout
- Pip cache
- npm cache
- Docker build (no push)

If you later add **Deploy** jobs (e.g. push to a registry or deploy to a server), you may need extra secrets or permissions; add those when you add that workflow.

---

## Quick checklist

- [ ] Repo has **Backend CI** and **Frontend CI** workflows under `.github/workflows/`.
- [ ] (Optional) Add `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` if tests should hit real Supabase.
- [ ] (Optional) Configure branch protection so PRs require these status checks.
