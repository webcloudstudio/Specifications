# Feature: S3 Company Share

| Field       | Value |
|-------------|-------|
| Version     | 20260528 V1 |
| Description | A deliberately simple per-user-prefix file share on S3 for the private circle of trust — read across the company, write only your own prefix. |
| Depends On  | FEATURE-MARINA-LIB.md, FEATURE-ACCESS-CONTROL.md |
| Provides    | GET /share, POST /share |

**Description:** A lightweight "share files with your company" feature. One private bucket partitioned by
member prefix; every member can read shared files, but can write only under their own prefix. Bytes move
directly to/from S3 via SigV4; the index is recorded in DynamoDB.

## Trigger

A member calls `mar.share.put(local_path, key)`, `mar.share.get(key, dest)`, or `mar.share.list(prefix)`.
No browser; no public objects.

## Sequence

**Put:**

1. `mar.share.put` resolves the destination key under `users/{member}/` (the member is the caller's Org
   identity), uploads bytes directly to `marina-{project}-share` via SigV4, then `POST /share` to record
   an index item (owner, key, size, content-type, updated_at) — bytes do not pass through Lambda.
2. IAM confines writes to the member's own prefix (`s3:PutObject` on `users/${aws:username}/*`); the
   bucket policy blocks all public access.

**List / Get:**

1. `GET /share` (optionally `?prefix=`) returns index items the principal may see (any `users/*` or
   `shared/*`). The principal must be an Org member; per-file read is open within the company.
2. `mar.share.get(key, dest)` downloads directly from S3 via SigV4 to the local destination.

## Reads

- `share_index` Lambda reads DynamoDB index items; the library reads S3 objects directly.
- ACL/Org-membership via the gate.

## Writes

- S3 object under the member's prefix (direct, SigV4); DynamoDB index item via `POST /share`.

## Test

- **Script:** `bin/test_s3_share.sh` → member A puts a file; asserts it appears in `GET /share` and member
  B can `get` it; asserts member B cannot write under member A's prefix (IAM denies); asserts no object is
  publicly readable.
- **Pass criteria:** cross-company read works; write confined to own prefix by IAM (not just library
  code); public access blocked; index reflects the object.
- **CloudWatch:** `share_index` log group emits `{"event":"share_put"/"share_list",...}`; S3 server
  access logs (or CloudTrail data events, if enabled) record the object operations.

## Open Questions

- Index in DynamoDB vs. listing S3 directly: the design indexes in DynamoDB to avoid `LIST` latency and
  to gate visibility — confirm this is worth the extra write, or accept plain `s3:ListBucket` for V1.
- Should there be a `shared/` company-wide drop space in addition to per-user prefixes? Cheap to add;
  include if members want a common area.
