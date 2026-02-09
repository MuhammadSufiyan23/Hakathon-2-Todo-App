# DB Schema Consistency Skill

Purpose:
Ensure database schema matches ORM and specs.

Activation:
- When database or models are modified

Procedure:
1. Verify tables and columns
2. Verify foreign keys and ownership
3. Verify indexes

Output:
- Schema consistency report

Quality Criteria:
- Data integrity preserved

## Verification Checklist
- [ ] ORM Models (e.g., SQLModel/Prisma) align with physical table structure
- [ ] Column names, types, and nullability match across all layers
- [ ] Foreign key constraints are correctly defined for relationship integrity
- [ ] Multi-tenant isolation (e.g., `user_id` or `workspace_id`) is strictly enforced in all tables
- [ ] Performance-critical indexes exist for frequent lookups
- [ ] Migration scripts exist and are applied for any schema changes
