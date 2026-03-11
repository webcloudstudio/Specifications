# AWS API Gateway Best Practices

Technology reference for Amazon API Gateway (HTTP API) with Lambda integration.
This file does not change between projects.

Prerequisites: `stack/aws-lambda.md`

Note: This file is included in the stack library for completeness. The
AlexaPrototypeOne project uses Lambda invoked directly by Alexa (not via
API Gateway). Use this reference when building HTTP-accessible Lambda endpoints.

---

## 1. REST API vs. HTTP API

**Rule**: TODO — Document the difference between REST API (v1) and HTTP API (v2).
HTTP API is cheaper (~70%), lower latency, and simpler. Use HTTP API unless
you need REST API-specific features (usage plans, request validation, etc.).

**Why**: TODO

---

## 2. Lambda Proxy Integration

**Rule**: TODO — Document the Lambda proxy integration format: how API Gateway
passes the HTTP request as an event dict, and how Lambda must return a specific
response dict format with statusCode, headers, and body.

```python
# TODO: Add Lambda proxy response format
# return {
#     "statusCode": 200,
#     "headers": {"Content-Type": "application/json"},
#     "body": json.dumps({"status": "ok"})
# }
```

**Why**: TODO

---

## 3. Stage Configuration

**Rule**: TODO — Document stage variables, default stage ($default for HTTP API),
and auto-deployment vs. manual deployment.

**Why**: TODO

---

## 4. CORS

**Rule**: TODO — Document CORS configuration for HTTP API, allowed origins/methods,
and the difference between simple and preflight requests.

**Why**: TODO

---

## 5. Authentication

**Rule**: TODO — Document API key auth (REST API), Lambda authorizer,
JWT authorizer (HTTP API), and IAM auth. Add decision table.

**Why**: TODO

---

## 6. CloudWatch Logging

**Rule**: TODO — Document access log format, execution logs,
and enabling logging on the stage.

**Why**: TODO

---

## 7. Throttling

**Rule**: TODO — Document default throttle limits (10,000 RPS burst, 5,000 RPS steady),
per-route throttling, and usage plans (REST API only).

**Why**: TODO

---

## Summary Checklist

- [ ] TODO: HTTP API (v2) preferred over REST API unless v1 features needed
- [ ] TODO: Lambda proxy integration used (not custom integration)
- [ ] TODO: CORS configured for browser-accessible endpoints
- [ ] TODO: Auth method selected and documented
- [ ] TODO: CloudWatch access logging enabled on stage
- [ ] TODO: Throttling limits reviewed for expected load
