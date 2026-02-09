---
id: 1
title: "Fix Auth Integration - Custom Endpoints"
stage: "red"
date_iso: "2026-01-16"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "master"
user: "king"
command: "/sp.implement"
labels: ["auth", "integration", "cors", "api"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "backend/main.py"
  - "frontend/lib/api.ts"
  - "frontend/lib/auth-client.ts"
  - "frontend/app/auth/signup/page.tsx"
  - "frontend/app/auth/signin/page.tsx"
tests_yaml: []
---

# Fix Auth Integration - Custom Endpoints

## Outcome
Fixed authentication integration issues by updating the frontend to use custom `/api/auth/*` endpoints instead of default Better Auth paths. Resolved CORS preflight issues by adding explicit OPTIONS handlers to the backend.

## Evaluation
- Fixed "Sign up failed" error by updating apiClient methods to use direct fetch to custom endpoints
- Fixed 405 Method Not Allowed on OPTIONS /api/sign-up/email by adding proper OPTIONS handlers
- Implemented proper token storage/retrieval in localStorage
- Maintained backward compatibility with existing imports
- All auth calls now properly route through custom endpoints: `/api/auth/signup`, `/api/auth/login`, etc.

## Prompt Text
```
IMPORTANT: Do NOT rewrite entire frontend or backend. Analyze the provided backend routes/auth.py, main.py, frontend lib/api.ts, auth-client.ts, utils.ts, signup page.tsx, and signin page.tsx. Fix ONLY the signup/signin "Sign up failed" error and 405 Method Not Allowed on OPTIONS /api/sign-up/email (default Better Auth path).

Current issues:
- Frontend still using Better Auth default paths (/api/sign-up/email, /api/sign-in/email) – causing OPTIONS 400/405 on backend (since custom /api/auth/signup exists)
- "Sign up failed" toast on submit – call not hitting custom endpoint
- Log: OPTIONS /api/sign-up/email 400, GET /api/auth/signup 405
- Cause: Frontend page onSubmit not triggering POST to custom endpoint, or residual Better Auth default behavior; backend not handling OPTIONS for default paths (but we will switch to custom)

Goal: Merge frontend/backend – frontend use custom /api/auth/signup (POST) and /api/auth/login (POST) via apiClient, backend handle OPTIONS for all /api/auth/*, ensure JWT/token with sub/userId/email

Analysis & Fix Steps:
1. Backend (/backend/):
   - routes/auth.py: Already good (POST /signup, /login with bcrypt, JWT encode with "sub", "userId")
   - main.py: Add explicit OPTIONS handlers if middleware not handling
     @app.options("/api/auth/{path:path}") async def options_auth(path: str): return {"detail": "OK"}

2. Frontend (/frontend/):
   - lib/api.ts: Good (request with authHeaders, signup/login as POST to /auth/signup, /auth/login – no token for auth)
   - lib/auth-client.ts: Remove or comment Better Auth client if not needed for session (since custom auth)
   - signup page.tsx: Use apiClient.signup(email, password) in handleSubmit (remove any Better Auth hooks)
   - signin page.tsx: Use apiClient.login(email, password) in handleSubmit
   - Remove any useAuth() or authClient.signUp.email() – direct apiClient use karo
   - Add console.log("Submitting to /api/auth/signup") in handleSubmit for debug

3. Integration:
   - No default Better Auth paths – all custom
   - After signup/login, store token in session (if not auto)
   - Test: Signup → backend user create + JWT return → frontend toast success + redirect

Output ONLY:
- Updated backend main.py snippet (add OPTIONS handler)
- Updated frontend signup page.tsx full code (with apiClient.signup)
- Updated frontend signin page.tsx full code (with apiClient.login)
- Updated lib/auth-client.ts if needed (comment Better Auth if not used for session)
- Instructions: "Replace files as shown. Restart frontend/backend. Clear browser cache (Ctrl+Shift+R). Test signup with new email – call POST /api/auth/signup hone chahiye, status 200/201, response with token. Then signin – dashboard pe redirect."

Do NOT output full files for unrelated parts or add new features.

Execute now – analyze and fix for proper custom auth integration!
```

## Response Text
Fixed authentication integration by:
1. Adding explicit OPTIONS handlers to backend main.py for all auth endpoints
2. Updating frontend api.ts to use direct fetch calls to custom endpoints instead of Better Auth client
3. Implementing proper token storage in localStorage
4. Commenting out Better Auth in auth-client.ts while maintaining compatibility
5. Ensuring all auth calls route through custom /api/auth/* endpoints