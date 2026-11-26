# Authentication Reference

Details for configuring API authentication headers during test runs.

## Bearer Tokens
Set `Authorization: Bearer <token>` using `API_TEST_TOKEN` from environment variables. Never log raw tokens.

## OAuth Refresh
If an endpoint returns `401 Unauthorized` once, exchange `API_REFRESH_TOKEN` at `POST /oauth/token` and retry the request once.

## HMAC Signing
When `X-Signature` is required, compute `HMAC-SHA256(secret, timestamp + method + path + body)` and attach `X-Timestamp` in Unix seconds.
