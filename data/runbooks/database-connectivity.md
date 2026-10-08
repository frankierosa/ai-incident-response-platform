# Runbook: Application Database Connectivity

## Purpose

Investigate application failures caused by database connectivity problems.

## Symptoms

* Application requests fail with database connection errors.
* Logs show connection refused, connection timeout, or authentication failures.
* Database-dependent operations fail or become slow.

## Investigation

1. Confirm the database service is running and accepting connections.
2. Verify the configured database hostname, port, and database name.
3. Confirm network connectivity from the application environment.
4. Check credentials and database authentication errors without exposing secrets.
5. Review database connection limits and application connection pool usage.
6. Inspect database logs for restarts, rejected connections, or resource exhaustion.

## Remediation

1. Restore database availability using the approved operational procedure.
2. Correct confirmed hostname, port, or configuration errors.
3. Resolve authentication problems through the approved secret-management process.
4. Address connection pool exhaustion or resource constraints based on evidence.

## Verification

* The application can establish database connections.
* Database-dependent API requests succeed.
* Connection errors return to normal levels.

## Escalation

Escalate to the database owner if the database is unavailable, connection limits are exhausted, or the cause cannot be established.

Never place database passwords or API keys in runbooks or logs.
