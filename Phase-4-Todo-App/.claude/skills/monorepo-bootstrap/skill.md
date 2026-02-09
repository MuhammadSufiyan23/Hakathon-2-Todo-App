# Monorepo Bootstrap Skill

Purpose:
Ensure the project follows the required Spec-Kit monorepo structure.

Activation:
- Automatically runs when a new phase or project is initialized

Procedure:
1. Verify presence of /specs, /frontend, /backend folders
2. Verify .spec-kit/config.yaml exists
3. Verify CLAUDE.md files at root and subfolders
4. Verify phase folders are isolated

Output:
- PASS / FAIL report
- List of missing or misconfigured folders

Quality Criteria:
- Structure matches Spec-Kit conventions
- No phase mixing

## Verification Checklist
- [/] `/specs` directory exists
- [/] `/frontend` directory exists
- [/] `/backend` directory exists
- [/] `.spec-kit/config.yaml` exists
- [/] `CLAUDE.md` exists at root
- [/] `CLAUDE.md` exists in subfolders
- [/] Phase isolation verified
