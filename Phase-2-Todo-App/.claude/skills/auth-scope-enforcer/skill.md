# Auth Scope Enforcer Skill

Purpose:
Ensure strict user data isolation.

Activation:
- On any data access logic

Procedure:
1. Verify user_id is derived from JWT
2. Verify all queries filter by user
3. Detect ID mismatch attempts

Output:
- Authorization enforcement report

Quality Criteria:
- No cross-user data access possible

## Verification Checklist
- [ ] `user_id` is extracted from the verified JWT payload only
- [ ] Every database query include a `.where(Model.user_id == current_user.id)` filter (or equivalent)
- [ ] No raw user IDs are accepted from request bodies or URLs without verifying ownership
- [ ] Multi-tenant isolation is applied at the lowest possible layer (e.g., repository or middleware)
- [ ] Attempting to access resources owned by another user returns 404 (Not Found) or 403 (Forbidden)
