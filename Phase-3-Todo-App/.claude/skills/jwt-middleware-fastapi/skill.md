# JWT Middleware FastAPI Skill

Purpose:
Validate JWT authentication behavior in FastAPI.

Activation:
- When auth or API implementation is discussed

Procedure:
1. Check Authorization: Bearer <token> usage
2. Validate token verification rules
3. Validate user extraction from JWT
4. Validate 401/403 error behavior

Output:
- JWT validation checklist
- Expected middleware behavior

Quality Criteria:
- Stateless auth
- User identity always enforced

## Verification Checklist
- [ ] OAuth2PasswordBearer scheme used
- [ ] Token signature verification (HS256/RS256)
- [ ] Expiration (exp) check
- [ ] User context extraction into dependency
- [ ] Proper 401 Unauthorized for invalid tokens
- [ ] Proper 403 Forbidden for insufficient scopes
