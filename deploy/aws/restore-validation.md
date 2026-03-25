# Managed PostgreSQL Restore Validation

1. Trigger an automated snapshot or confirm the most recent managed backup timestamp.
2. Restore the backup into a non-production database instance.
3. Point a temporary backend container at the restored database with `POSTGRES_DSN`.
4. Run the backend smoke checks and `pytest tests/integration`.
5. Confirm expert profiles, search documents, and outreach records are present.
6. Record the backup age and restore duration to verify the `RPO < 24h` and `RTO < 1h` targets.

This procedure is documented here, but it still requires execution in the target AWS account.
