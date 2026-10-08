# Runbook: Payment Service HTTP 500 Errors

## Purpose

Investigate HTTP 500 responses returned by the payment service.

## Symptoms

* Customers cannot complete payment transactions.
* Requests to the payment API return HTTP 500.
* Application logs contain unhandled exceptions or dependency failures.

## Investigation

1. Check payment service health and recent error rates.
2. Review application logs around the incident start time.
3. Check recent deployments and configuration changes.
4. Verify connectivity to the database and other required dependencies.
5. Check dependency latency, timeouts, and connection pool exhaustion.

## Remediation

1. If a recent deployment correlates with the incident, evaluate rollback according to the team's deployment procedure.
2. Restore unavailable dependencies using their approved recovery procedures.
3. Correct confirmed configuration or application errors.
4. Verify payment requests succeed after remediation.

## Verification

* HTTP 500 rates return to normal.
* Payment transactions succeed.
* Dependency health and latency return to acceptable levels.
* Continue monitoring before declaring the incident resolved.

## Escalation

Escalate to the payment service owner if the cause remains unclear, failures continue after remediation, or customer impact is increasing.

Do not assume the root cause until logs and system evidence support it.
