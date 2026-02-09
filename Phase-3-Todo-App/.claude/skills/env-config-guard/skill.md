# Env Config Guard Skill

Purpose:
Ensure environment variables are correctly defined.

Activation:
- When running or deploying services

Procedure:
1. Check required env vars
2. Validate secrets are not hard-coded
3. Validate dev vs prod separation

Output:
- Env validation checklist

Quality Criteria:
- Secure configuration

## Verification Checklist
- [ ] `.env.example` exists and is up to date with required variables
- [ ] No secrets (keys, tokens, passwords) are hard-coded in the source code
- [ ] `.env` is listed in `.gitignore`
- [ ] Development variables are clearly separated from production variables
- [ ] Variable naming follows the standard convention (e.g., `DATABASE_URL`, `JWT_SECRET`)
- [ ] All required variables for the current environment are populated
