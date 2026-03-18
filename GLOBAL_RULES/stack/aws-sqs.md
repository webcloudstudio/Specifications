# AWS SQS Best Practices

Technology reference for Amazon SQS message queues with Python (boto3).
This file does not change between projects.

Prerequisites: `stack/python.md`

---

## 1. Queue Types: Standard vs. FIFO

**Rule**: TODO — Document when to use Standard (at-least-once, best-effort ordering)
vs. FIFO (exactly-once, strict ordering). Add decision table.

**Why**: TODO

---

## 2. boto3 Client Setup

**Rule**: TODO — Document client creation, region configuration,
and credential resolution order (env vars → IAM role → profile).

```python
# TODO: Add boto3 client setup pattern
# import boto3
# sqs = boto3.client('sqs', region_name=os.environ['AWS_REGION'])
```

**Why**: TODO

---

## 3. Send Message

**Rule**: TODO — Document send_message parameters, MessageBody formatting,
MessageAttributes usage, and MessageGroupId for FIFO.

```python
# TODO: Add send_message example
```

**Why**: TODO

---

## 4. Receive Message (Long Polling)

**Rule**: TODO — Document receive_message parameters, why WaitTimeSeconds=20
reduces cost and improves latency, MaxNumberOfMessages (1–10), and VisibilityTimeout.

```python
# TODO: Add receive_message long-polling example
# response = sqs.receive_message(
#     QueueUrl=QUEUE_URL,
#     MaxNumberOfMessages=10,
#     WaitTimeSeconds=20,
# )
```

**Why**: TODO

---

## 5. Delete Message After Processing

**Rule**: TODO — Document that messages must be explicitly deleted using the
ReceiptHandle, and that deletion only happens after successful processing
(outbox pattern).

```python
# TODO: Add delete_message example
```

**Why**: TODO

---

## 6. Visibility Timeout (Retry Without Delete)

**Rule**: TODO — Document how visibility timeout enables retry-without-delete
for failure handling, change_message_visibility for extending holds (e.g.,
pending confirmations), and DLQ thresholds.

**Why**: TODO

---

## 7. Dead Letter Queue Configuration

**Rule**: TODO — Document DLQ setup (Standard queue, maxReceiveCount),
monitoring the DLQ, and when to manually replay vs. discard DLQ messages.

**Why**: TODO

---

## 8. Queue Depth Monitoring

**Rule**: TODO — Document get_queue_attributes for ApproximateNumberOfMessages
and ApproximateNumberOfMessagesNotVisible, and how to expose these in dashboards.

```python
# TODO: Add get_queue_attributes example
```

**Why**: TODO

---

## Summary Checklist

- [ ] TODO: Standard queue for at-least-once; FIFO only when ordering required
- [ ] TODO: Long polling (WaitTimeSeconds=20) always enabled
- [ ] TODO: MaxNumberOfMessages=10 for batch efficiency
- [ ] TODO: Messages deleted only after confirmed successful processing
- [ ] TODO: DLQ configured with maxReceiveCount=3
- [ ] TODO: VisibilityTimeout > longest expected processing time
- [ ] TODO: Queue URL stored in env var, never hardcoded
- [ ] TODO: IAM policy scoped to specific queue ARN
