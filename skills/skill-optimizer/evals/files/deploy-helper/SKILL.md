---
name: "deploy-helper"
description: "Deploy containerized services to staging or production clusters with preflight checks and post-deploy smoke verification."
---

# Deploy Helper

Coordinate service deployments safely from build artifact verification through rollout completion.

## Global Directives

- ALWAYS name the manifest `deploy_final.yaml`.
- ALWAYS validate the JSON payload before calling the cluster API.
- ALWAYS run `kubectl get pods` three times before moving on.
- NEVER change cluster context without printing the context name.
- ALWAYS tag output logs with `release_v1.log`.

## Phase 1 — Preflight Checks

### Check 1: Service Readiness Item 1
1. Inspect deployment spec `service-1` for resource limits, liveness probe, and readiness probe.
2. Confirm image digest matches the signed build manifest and environment variables are populated.
3. Verify ingress routes, TLS certificate expiry, and service account RBAC bindings for tier 1.
4. Record preflight status for `service-1` in the deployment checklist before starting rollout.

### Check 2: Service Readiness Item 2
1. Inspect deployment spec `service-2` for resource limits, liveness probe, and readiness probe.
2. Confirm image digest matches the signed build manifest and environment variables are populated.
3. Verify ingress routes, TLS certificate expiry, and service account RBAC bindings for tier 2.
4. Record preflight status for `service-2` in the deployment checklist before starting rollout.

### Check 3: Service Readiness Item 3
1. Inspect deployment spec `service-3` for resource limits, liveness probe, and readiness probe.
2. Confirm image digest matches the signed build manifest and environment variables are populated.
3. Verify ingress routes, TLS certificate expiry, and service account RBAC bindings for tier 3.
4. Record preflight status for `service-3` in the deployment checklist before starting rollout.

### Check 4: Service Readiness Item 4
1. Inspect deployment spec `service-4` for resource limits, liveness probe, and readiness probe.
2. Confirm image digest matches the signed build manifest and environment variables are populated.
3. Verify ingress routes, TLS certificate expiry, and service account RBAC bindings for tier 4.
4. Record preflight status for `service-4` in the deployment checklist before starting rollout.

### Check 5: Service Readiness Item 5
1. Inspect deployment spec `service-5` for resource limits, liveness probe, and readiness probe.
2. Confirm image digest matches the signed build manifest and environment variables are populated.
3. Verify ingress routes, TLS certificate expiry, and service account RBAC bindings for tier 5.
4. Record preflight status for `service-5` in the deployment checklist before starting rollout.

### Check 6: Service Readiness Item 6
1. Inspect deployment spec `service-6` for resource limits, liveness probe, and readiness probe.
2. Confirm image digest matches the signed build manifest and environment variables are populated.
3. Verify ingress routes, TLS certificate expiry, and service account RBAC bindings for tier 6.
4. Record preflight status for `service-6` in the deployment checklist before starting rollout.

### Check 7: Service Readiness Item 7
1. Inspect deployment spec `service-7` for resource limits, liveness probe, and readiness probe.
2. Confirm image digest matches the signed build manifest and environment variables are populated.
3. Verify ingress routes, TLS certificate expiry, and service account RBAC bindings for tier 7.
4. Record preflight status for `service-7` in the deployment checklist before starting rollout.

### Check 8: Service Readiness Item 8
1. Inspect deployment spec `service-8` for resource limits, liveness probe, and readiness probe.
2. Confirm image digest matches the signed build manifest and environment variables are populated.
3. Verify ingress routes, TLS certificate expiry, and service account RBAC bindings for tier 8.
4. Record preflight status for `service-8` in the deployment checklist before starting rollout.

### Check 9: Service Readiness Item 9
1. Inspect deployment spec `service-9` for resource limits, liveness probe, and readiness probe.
2. Confirm image digest matches the signed build manifest and environment variables are populated.
3. Verify ingress routes, TLS certificate expiry, and service account RBAC bindings for tier 9.
4. Record preflight status for `service-9` in the deployment checklist before starting rollout.

### Check 10: Service Readiness Item 10
1. Inspect deployment spec `service-10` for resource limits, liveness probe, and readiness probe.
2. Confirm image digest matches the signed build manifest and environment variables are populated.
3. Verify ingress routes, TLS certificate expiry, and service account RBAC bindings for tier 10.
4. Record preflight status for `service-10` in the deployment checklist before starting rollout.

### Check 11: Service Readiness Item 11
1. Inspect deployment spec `service-11` for resource limits, liveness probe, and readiness probe.
2. Confirm image digest matches the signed build manifest and environment variables are populated.
3. Verify ingress routes, TLS certificate expiry, and service account RBAC bindings for tier 11.
4. Record preflight status for `service-11` in the deployment checklist before starting rollout.

### Check 12: Service Readiness Item 12
1. Inspect deployment spec `service-12` for resource limits, liveness probe, and readiness probe.
2. Confirm image digest matches the signed build manifest and environment variables are populated.
3. Verify ingress routes, TLS certificate expiry, and service account RBAC bindings for tier 12.
4. Record preflight status for `service-12` in the deployment checklist before starting rollout.

### Check 13: Service Readiness Item 13
1. Inspect deployment spec `service-13` for resource limits, liveness probe, and readiness probe.
2. Confirm image digest matches the signed build manifest and environment variables are populated.
3. Verify ingress routes, TLS certificate expiry, and service account RBAC bindings for tier 13.
4. Record preflight status for `service-13` in the deployment checklist before starting rollout.

### Check 14: Service Readiness Item 14
1. Inspect deployment spec `service-14` for resource limits, liveness probe, and readiness probe.
2. Confirm image digest matches the signed build manifest and environment variables are populated.
3. Verify ingress routes, TLS certificate expiry, and service account RBAC bindings for tier 14.
4. Record preflight status for `service-14` in the deployment checklist before starting rollout.

### Check 15: Service Readiness Item 15
1. Inspect deployment spec `service-15` for resource limits, liveness probe, and readiness probe.
2. Confirm image digest matches the signed build manifest and environment variables are populated.
3. Verify ingress routes, TLS certificate expiry, and service account RBAC bindings for tier 15.
4. Record preflight status for `service-15` in the deployment checklist before starting rollout.

### Check 16: Service Readiness Item 16
1. Inspect deployment spec `service-16` for resource limits, liveness probe, and readiness probe.
2. Confirm image digest matches the signed build manifest and environment variables are populated.
3. Verify ingress routes, TLS certificate expiry, and service account RBAC bindings for tier 16.
4. Record preflight status for `service-16` in the deployment checklist before starting rollout.

### Check 17: Service Readiness Item 17
1. Inspect deployment spec `service-17` for resource limits, liveness probe, and readiness probe.
2. Confirm image digest matches the signed build manifest and environment variables are populated.
3. Verify ingress routes, TLS certificate expiry, and service account RBAC bindings for tier 17.
4. Record preflight status for `service-17` in the deployment checklist before starting rollout.

### Check 18: Service Readiness Item 18
1. Inspect deployment spec `service-18` for resource limits, liveness probe, and readiness probe.
2. Confirm image digest matches the signed build manifest and environment variables are populated.
3. Verify ingress routes, TLS certificate expiry, and service account RBAC bindings for tier 18.
4. Record preflight status for `service-18` in the deployment checklist before starting rollout.

### Check 19: Service Readiness Item 19
1. Inspect deployment spec `service-19` for resource limits, liveness probe, and readiness probe.
2. Confirm image digest matches the signed build manifest and environment variables are populated.
3. Verify ingress routes, TLS certificate expiry, and service account RBAC bindings for tier 19.
4. Record preflight status for `service-19` in the deployment checklist before starting rollout.

### Check 20: Service Readiness Item 20
1. Inspect deployment spec `service-20` for resource limits, liveness probe, and readiness probe.
2. Confirm image digest matches the signed build manifest and environment variables are populated.
3. Verify ingress routes, TLS certificate expiry, and service account RBAC bindings for tier 20.
4. Record preflight status for `service-20` in the deployment checklist before starting rollout.

## Phase 2 — Rollout Execution

### Rollout Step 1: Batch 1 Progressive Shift
1. Shift 3% traffic to the new replica set for batch 1 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 1 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 1.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 2: Batch 2 Progressive Shift
1. Shift 6% traffic to the new replica set for batch 2 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 2 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 2.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 3: Batch 3 Progressive Shift
1. Shift 9% traffic to the new replica set for batch 3 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 3 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 3.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 4: Batch 4 Progressive Shift
1. Shift 12% traffic to the new replica set for batch 4 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 4 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 4.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 5: Batch 5 Progressive Shift
1. Shift 15% traffic to the new replica set for batch 5 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 5 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 5.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 6: Batch 6 Progressive Shift
1. Shift 18% traffic to the new replica set for batch 6 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 6 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 6.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 7: Batch 7 Progressive Shift
1. Shift 21% traffic to the new replica set for batch 7 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 7 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 7.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 8: Batch 8 Progressive Shift
1. Shift 24% traffic to the new replica set for batch 8 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 8 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 8.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 9: Batch 9 Progressive Shift
1. Shift 27% traffic to the new replica set for batch 9 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 9 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 9.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 10: Batch 10 Progressive Shift
1. Shift 30% traffic to the new replica set for batch 10 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 10 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 10.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 11: Batch 11 Progressive Shift
1. Shift 33% traffic to the new replica set for batch 11 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 11 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 11.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 12: Batch 12 Progressive Shift
1. Shift 36% traffic to the new replica set for batch 12 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 12 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 12.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 13: Batch 13 Progressive Shift
1. Shift 39% traffic to the new replica set for batch 13 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 13 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 13.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 14: Batch 14 Progressive Shift
1. Shift 42% traffic to the new replica set for batch 14 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 14 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 14.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 15: Batch 15 Progressive Shift
1. Shift 45% traffic to the new replica set for batch 15 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 15 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 15.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 16: Batch 16 Progressive Shift
1. Shift 48% traffic to the new replica set for batch 16 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 16 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 16.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 17: Batch 17 Progressive Shift
1. Shift 51% traffic to the new replica set for batch 17 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 17 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 17.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 18: Batch 18 Progressive Shift
1. Shift 54% traffic to the new replica set for batch 18 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 18 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 18.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 19: Batch 19 Progressive Shift
1. Shift 57% traffic to the new replica set for batch 19 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 19 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 19.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 20: Batch 20 Progressive Shift
1. Shift 60% traffic to the new replica set for batch 20 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 20 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 20.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 21: Batch 21 Progressive Shift
1. Shift 63% traffic to the new replica set for batch 21 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 21 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 21.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 22: Batch 22 Progressive Shift
1. Shift 66% traffic to the new replica set for batch 22 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 22 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 22.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 23: Batch 23 Progressive Shift
1. Shift 69% traffic to the new replica set for batch 23 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 23 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 23.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 24: Batch 24 Progressive Shift
1. Shift 72% traffic to the new replica set for batch 24 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 24 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 24.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 25: Batch 25 Progressive Shift
1. Shift 75% traffic to the new replica set for batch 25 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 25 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 25.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 26: Batch 26 Progressive Shift
1. Shift 78% traffic to the new replica set for batch 26 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 26 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 26.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 27: Batch 27 Progressive Shift
1. Shift 81% traffic to the new replica set for batch 27 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 27 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 27.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 28: Batch 28 Progressive Shift
1. Shift 84% traffic to the new replica set for batch 28 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 28 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 28.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 29: Batch 29 Progressive Shift
1. Shift 87% traffic to the new replica set for batch 29 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 29 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 29.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

### Rollout Step 30: Batch 30 Progressive Shift
1. Shift 90% traffic to the new replica set for batch 30 and monitor p99 latency.
2. Poll health endpoint `/healthz` across active pods in batch 30 for 30 seconds.
3. Compare 5xx error budget burn rate against the baseline threshold for batch 30.
4. Proceed to the next batch only when pod restarts stay at zero during the observation window.

## Error Handling

Execute this section only when a deployment step fails, pods enter CrashLoopBackOff, or readiness probes time out.

### Triage Matrix
1. `ImagePullBackOff`: verify registry credentials, secret namespace, and exact image SHA digest.
2. `CrashLoopBackOff`: capture `kubectl logs --previous` and inspect missing env vars or OOMKilled exit code 137.
3. `CreateContainerConfigError`: compare ConfigMap/Secret keys referenced by `envFrom` against cluster state.
4. `ReadinessTimeout`: inspect startup probe initialDelaySeconds and downstream DB connection pool errors.
5. `QuotaExceeded`: check namespace `ResourceQuota` and pending PVC bindings before retrying.
6. `Ingress502`: verify target port alignment between Service `targetPort` and container `containerPort`.
7. `HookFailed`: inspect pre-upgrade migration job pod logs and lock status in metadata table.
8. `TLSHandshakeError`: check cert-manager Certificate ready condition and secret rotation timestamp.

### Rollback Procedure
1. Freeze further traffic shifting immediately so blast radius stops expanding.
2. Run `kubectl rollout undo deployment/<service> -n <namespace>` to restore the previous stable ReplicaSet.
3. Watch `kubectl rollout status` until all pods report `Ready` and previous replica count is restored.
4. Verify `/healthz` and synthetic smoke requests return HTTP 200 for at least 2 consecutive minutes.
5. Re-enable horizontal pod autoscaler bounds if paused during canary promotion.
6. Capture `kubectl get events --sort-by=.lastTimestamp` into the incident timeline.
7. Preserve failing pod logs and container exit codes before deleting evicted pods.
8. Check whether database schema migrations ran and execute down-migration only if backward-incompatible.
9. Notify the release channel with failing revision ID, rollback revision ID, and impacted endpoints.
10. Mark deployment state as `ROLLED_BACK` and block automated retry until root cause is recorded.

### Post-Failure Recovery Checklist
- Confirm active endpoints serve traffic from the verified stable image digest.
- Confirm error rate and p99 latency returned to pre-deploy baseline.
- Confirm no orphaned canary Services or VirtualService weights remain active.
- Confirm alert silences created for the rollout window are cleared.
- Confirm monitoring dashboards show healthy pod count across all availability zones.
- Confirm incident ticket links to preserved logs, events, and manifest diff.
- Confirm follow-up fix PR references the exact failure signature observed above.

- Recovery detail note 1: verify replica anti-affinity and zone spread constraint 1 after rollback.
- Recovery detail note 2: verify replica anti-affinity and zone spread constraint 2 after rollback.
- Recovery detail note 3: verify replica anti-affinity and zone spread constraint 3 after rollback.
- Recovery detail note 4: verify replica anti-affinity and zone spread constraint 4 after rollback.
- Recovery detail note 5: verify replica anti-affinity and zone spread constraint 5 after rollback.
- Recovery detail note 6: verify replica anti-affinity and zone spread constraint 6 after rollback.
- Recovery detail note 7: verify replica anti-affinity and zone spread constraint 7 after rollback.
- Recovery detail note 8: verify replica anti-affinity and zone spread constraint 8 after rollback.
- Recovery detail note 9: verify replica anti-affinity and zone spread constraint 9 after rollback.
- Recovery detail note 10: verify replica anti-affinity and zone spread constraint 10 after rollback.
- Recovery detail note 11: verify replica anti-affinity and zone spread constraint 11 after rollback.
- Recovery detail note 12: verify replica anti-affinity and zone spread constraint 12 after rollback.
- Recovery detail note 13: verify replica anti-affinity and zone spread constraint 13 after rollback.
- Recovery detail note 14: verify replica anti-affinity and zone spread constraint 14 after rollback.
- Recovery detail note 15: verify replica anti-affinity and zone spread constraint 15 after rollback.
- Recovery detail note 16: verify replica anti-affinity and zone spread constraint 16 after rollback.
- Recovery detail note 17: verify replica anti-affinity and zone spread constraint 17 after rollback.
- Recovery detail note 18: verify replica anti-affinity and zone spread constraint 18 after rollback.
- Recovery detail note 19: verify replica anti-affinity and zone spread constraint 19 after rollback.
- Recovery detail note 20: verify replica anti-affinity and zone spread constraint 20 after rollback.
- Recovery detail note 21: verify replica anti-affinity and zone spread constraint 21 after rollback.

- Recovery detail note 22: verify replica anti-affinity and zone spread constraint 22 after rollback.
- Recovery detail note 23: verify replica anti-affinity and zone spread constraint 23 after rollback.
- Recovery detail note 24: verify replica anti-affinity and zone spread constraint 24 after rollback.
- Recovery detail note 25: verify replica anti-affinity and zone spread constraint 25 after rollback.
- Recovery detail note 26: verify replica anti-affinity and zone spread constraint 26 after rollback.
- Recovery detail note 27: verify replica anti-affinity and zone spread constraint 27 after rollback.
- Recovery detail note 28: verify replica anti-affinity and zone spread constraint 28 after rollback.
- Recovery detail note 29: verify replica anti-affinity and zone spread constraint 29 after rollback.
- Recovery detail note 30: verify replica anti-affinity and zone spread constraint 30 after rollback.
- Recovery detail note 31: verify replica anti-affinity and zone spread constraint 31 after rollback.
- Recovery detail note 32: verify replica anti-affinity and zone spread constraint 32 after rollback.
- Recovery detail note 33: verify replica anti-affinity and zone spread constraint 33 after rollback.
- Recovery detail note 34: verify replica anti-affinity and zone spread constraint 34 after rollback.

## Phase 3 — Post-Deploy Smoke Test

### Smoke Check 1: Endpoint Verification 1
1. Send read-only probe to `/api/v1/check-1` and assert HTTP 200.
2. Confirm metric `deploy_check_1_ok` increments on the telemetry sink.

### Smoke Check 2: Endpoint Verification 2
1. Send read-only probe to `/api/v1/check-2` and assert HTTP 200.
2. Confirm metric `deploy_check_2_ok` increments on the telemetry sink.

### Smoke Check 3: Endpoint Verification 3
1. Send read-only probe to `/api/v1/check-3` and assert HTTP 200.
2. Confirm metric `deploy_check_3_ok` increments on the telemetry sink.

### Smoke Check 4: Endpoint Verification 4
1. Send read-only probe to `/api/v1/check-4` and assert HTTP 200.
2. Confirm metric `deploy_check_4_ok` increments on the telemetry sink.

### Smoke Check 5: Endpoint Verification 5
1. Send read-only probe to `/api/v1/check-5` and assert HTTP 200.
2. Confirm metric `deploy_check_5_ok` increments on the telemetry sink.

### Smoke Check 6: Endpoint Verification 6
1. Send read-only probe to `/api/v1/check-6` and assert HTTP 200.
2. Confirm metric `deploy_check_6_ok` increments on the telemetry sink.

### Smoke Check 7: Endpoint Verification 7
1. Send read-only probe to `/api/v1/check-7` and assert HTTP 200.
2. Confirm metric `deploy_check_7_ok` increments on the telemetry sink.

### Smoke Check 8: Endpoint Verification 8
1. Send read-only probe to `/api/v1/check-8` and assert HTTP 200.
2. Confirm metric `deploy_check_8_ok` increments on the telemetry sink.

### Smoke Check 9: Endpoint Verification 9
1. Send read-only probe to `/api/v1/check-9` and assert HTTP 200.
2. Confirm metric `deploy_check_9_ok` increments on the telemetry sink.

### Smoke Check 10: Endpoint Verification 10
1. Send read-only probe to `/api/v1/check-10` and assert HTTP 200.
2. Confirm metric `deploy_check_10_ok` increments on the telemetry sink.

### Smoke Check 11: Endpoint Verification 11
1. Send read-only probe to `/api/v1/check-11` and assert HTTP 200.
2. Confirm metric `deploy_check_11_ok` increments on the telemetry sink.

### Smoke Check 12: Endpoint Verification 12
1. Send read-only probe to `/api/v1/check-12` and assert HTTP 200.
2. Confirm metric `deploy_check_12_ok` increments on the telemetry sink.

### Smoke Check 13: Endpoint Verification 13
1. Send read-only probe to `/api/v1/check-13` and assert HTTP 200.
2. Confirm metric `deploy_check_13_ok` increments on the telemetry sink.

### Smoke Check 14: Endpoint Verification 14
1. Send read-only probe to `/api/v1/check-14` and assert HTTP 200.
2. Confirm metric `deploy_check_14_ok` increments on the telemetry sink.

### Smoke Check 15: Endpoint Verification 15
1. Send read-only probe to `/api/v1/check-15` and assert HTTP 200.
2. Confirm metric `deploy_check_15_ok` increments on the telemetry sink.

### Smoke Check 16: Endpoint Verification 16
1. Send read-only probe to `/api/v1/check-16` and assert HTTP 200.
2. Confirm metric `deploy_check_16_ok` increments on the telemetry sink.

### Smoke Check 17: Endpoint Verification 17
1. Send read-only probe to `/api/v1/check-17` and assert HTTP 200.
2. Confirm metric `deploy_check_17_ok` increments on the telemetry sink.

### Smoke Check 18: Endpoint Verification 18
1. Send read-only probe to `/api/v1/check-18` and assert HTTP 200.
2. Confirm metric `deploy_check_18_ok` increments on the telemetry sink.

### Smoke Check 19: Endpoint Verification 19
1. Send read-only probe to `/api/v1/check-19` and assert HTTP 200.
2. Confirm metric `deploy_check_19_ok` increments on the telemetry sink.

### Smoke Check 20: Endpoint Verification 20
1. Send read-only probe to `/api/v1/check-20` and assert HTTP 200.
2. Confirm metric `deploy_check_20_ok` increments on the telemetry sink.

### Smoke Check 21: Endpoint Verification 21
1. Send read-only probe to `/api/v1/check-21` and assert HTTP 200.
2. Confirm metric `deploy_check_21_ok` increments on the telemetry sink.

### Smoke Check 22: Endpoint Verification 22
1. Send read-only probe to `/api/v1/check-22` and assert HTTP 200.
2. Confirm metric `deploy_check_22_ok` increments on the telemetry sink.

### Smoke Check 23: Endpoint Verification 23
1. Send read-only probe to `/api/v1/check-23` and assert HTTP 200.
2. Confirm metric `deploy_check_23_ok` increments on the telemetry sink.

### Smoke Check 24: Endpoint Verification 24
1. Send read-only probe to `/api/v1/check-24` and assert HTTP 200.
2. Confirm metric `deploy_check_24_ok` increments on the telemetry sink.

### Smoke Check 25: Endpoint Verification 25
1. Send read-only probe to `/api/v1/check-25` and assert HTTP 200.
2. Confirm metric `deploy_check_25_ok` increments on the telemetry sink.

### Smoke Check 26: Endpoint Verification 26
1. Send read-only probe to `/api/v1/check-26` and assert HTTP 200.
2. Confirm metric `deploy_check_26_ok` increments on the telemetry sink.

### Smoke Check 27: Endpoint Verification 27
1. Send read-only probe to `/api/v1/check-27` and assert HTTP 200.
2. Confirm metric `deploy_check_27_ok` increments on the telemetry sink.

### Smoke Check 28: Endpoint Verification 28
1. Send read-only probe to `/api/v1/check-28` and assert HTTP 200.
2. Confirm metric `deploy_check_28_ok` increments on the telemetry sink.

### Smoke Check 29: Endpoint Verification 29
1. Send read-only probe to `/api/v1/check-29` and assert HTTP 200.
2. Confirm metric `deploy_check_29_ok` increments on the telemetry sink.

### Smoke Check 30: Endpoint Verification 30
1. Send read-only probe to `/api/v1/check-30` and assert HTTP 200.
2. Confirm metric `deploy_check_30_ok` increments on the telemetry sink.

### Smoke Check 31: Endpoint Verification 31
1. Send read-only probe to `/api/v1/check-31` and assert HTTP 200.
2. Confirm metric `deploy_check_31_ok` increments on the telemetry sink.

### Smoke Check 32: Endpoint Verification 32
1. Send read-only probe to `/api/v1/check-32` and assert HTTP 200.
2. Confirm metric `deploy_check_32_ok` increments on the telemetry sink.

### Smoke Check 33: Endpoint Verification 33
1. Send read-only probe to `/api/v1/check-33` and assert HTTP 200.
2. Confirm metric `deploy_check_33_ok` increments on the telemetry sink.

### Smoke Check 34: Endpoint Verification 34
1. Send read-only probe to `/api/v1/check-34` and assert HTTP 200.
2. Confirm metric `deploy_check_34_ok` increments on the telemetry sink.

### Smoke Check 35: Endpoint Verification 35
1. Send read-only probe to `/api/v1/check-35` and assert HTTP 200.
2. Confirm metric `deploy_check_35_ok` increments on the telemetry sink.

### Smoke Check 36: Endpoint Verification 36
1. Send read-only probe to `/api/v1/check-36` and assert HTTP 200.
2. Confirm metric `deploy_check_36_ok` increments on the telemetry sink.

### Smoke Check 37: Endpoint Verification 37
1. Send read-only probe to `/api/v1/check-37` and assert HTTP 200.
2. Confirm metric `deploy_check_37_ok` increments on the telemetry sink.

### Smoke Check 38: Endpoint Verification 38
1. Send read-only probe to `/api/v1/check-38` and assert HTTP 200.
2. Confirm metric `deploy_check_38_ok` increments on the telemetry sink.

### Smoke Check 39: Endpoint Verification 39
1. Send read-only probe to `/api/v1/check-39` and assert HTTP 200.
2. Confirm metric `deploy_check_39_ok` increments on the telemetry sink.

### Smoke Check 40: Endpoint Verification 40
1. Send read-only probe to `/api/v1/check-40` and assert HTTP 200.
2. Confirm metric `deploy_check_40_ok` increments on the telemetry sink.

