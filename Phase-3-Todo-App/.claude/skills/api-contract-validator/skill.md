# API Contract Validator Skill

Purpose:
Ensure frontend and backend follow the same API contract.

Activation:
- When API endpoints are implemented

Procedure:
1. Compare API specs with backend routes
2. Compare API specs with frontend usage
3. Validate HTTP methods and status codes

Output:
- Contract mismatch report

Quality Criteria:
- Zero breaking mismatches

## Verification Checklist
- [ ] Backend route URL matches the specification
- [ ] Backend request/response schemas match the specification
- [ ] Frontend request/response types (TypeScript) match the specification
- [ ] HTTP Methods (GET, POST, etc.) are consistent across all layers
- [ ] Success and Error status codes (e.g., 200, 201, 400, 401, 500) match
- [ ] Query parameters and path variables are identically named and typed
