# AWS Lambda Best Practices

**Version:** 20260320 V1
**Description:** AWS Lambda deployment patterns: handlers, events, and packaging

Technology reference for AWS Lambda functions in Python.
This file does not change between projects.

Prerequisites: `stack/python.md`

---

## 1. Handler Signature

**Rule**: TODO — Define the canonical Lambda handler signature and event/context usage.

```python
# TODO: Add canonical handler signature
# def lambda_handler(event: dict, context) -> dict:
#     ...
```

**Why**: TODO

---

## 2. Environment Variables

**Rule**: TODO — Document how to read env vars in Lambda and the difference from
local .env files (Lambda does not use .env; vars are set in console/config).

```python
# TODO: Add env var access pattern
```

**Why**: TODO

---

## 3. IAM Least Privilege

**Rule**: TODO — Document inline policy patterns, execution role creation,
and how to scope permissions to specific resource ARNs.

```json
// TODO: Add IAM policy example
```

**Why**: TODO

---

## 4. Timeout and Memory Sizing

**Rule**: TODO — Provide sizing guidance based on workload type.
Add table of recommended values for common use cases (API proxy, SQS writer, data processor).

**Why**: TODO

---

## 5. Alexa Request Validation

**Rule**: TODO — Document skill ID validation, request signature verification,
and timestamp verification (prevent replay attacks).

```python
# TODO: Add request validation pattern
```

**Why**: TODO

---

## 6. Error Handling and Dead Letter Queues

**Rule**: TODO — Document try/except structure in handler, what to return on error,
and how to configure a DLQ for async invocations.

**Why**: TODO

---

## 7. Deployment (Zip Upload)

**Rule**: TODO — Document zip packaging for Python, handling dependencies
(layer vs. bundled), and the aws lambda update-function-code workflow.

```bash
# TODO: Add deployment commands
```

**Why**: TODO

---

## 8. CloudWatch Logging

**Rule**: TODO — Document the logging module setup for Lambda,
log level configuration, and how to view logs in CloudWatch console.

```python
# TODO: Add logging setup
```

**Why**: TODO

---

## Summary Checklist

- [ ] TODO: Handler validates event type before processing
- [ ] TODO: Skill/source ID validated before execution
- [ ] TODO: Timeout set to minimum needed (not default 3s or 15min)
- [ ] TODO: Memory tuned to workload
- [ ] TODO: IAM role uses least-privilege inline policy
- [ ] TODO: All env vars documented in STACK.yaml
- [ ] TODO: DLQ configured for async invocations
- [ ] TODO: CloudWatch log group retention set (not infinite)
