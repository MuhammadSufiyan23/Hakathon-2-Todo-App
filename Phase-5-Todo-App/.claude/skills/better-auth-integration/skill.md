# Better Auth Integration Skill

Purpose:
Ensure Better Auth issues and manages JWTs correctly.

Activation:
- When frontend auth is involved

Procedure:
1. Verify JWT issuance is enabled
2. Verify token expiry handling
3. Verify token storage method
4. Verify frontend attaches token to API calls

Output:
- Integration validation report

Quality Criteria:
- Secure token handling
- No frontend-backend auth mismatch

## Verification Checklist
- [ ] `jwt` plugin is enabled in Better Auth configuration
- [ ] Token expiration matches security requirements (e.g., 24h)
- [ ] Cookies are set to `HttpOnly`, `Secure`, and `SameSite: Lax/Strict`
- [ ] API client (fetch/axios wrapper) correctly extracts and attaches the token
- [ ] Frontend handles 401 Unauthorized by clearing session or redirecting
- [ ] Backend is using the same secret/public key to verify the token
