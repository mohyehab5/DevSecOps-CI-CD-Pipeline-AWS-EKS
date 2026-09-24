# AWS WAFv2 — Rule Groups Attached to the Ingress ALB

Referenced by `kubernetes/ingress.yaml` via `alb.ingress.kubernetes.io/wafv2-acl-arn`.

| Managed Rule Group | Purpose |
|---|---|
| `AWSManagedRulesCommonRuleSet` | Blocks generic OWASP Top 10 patterns (XSS, LFI, oversized bodies) |
| `AWSManagedRulesKnownBadInputsRuleSet` | Blocks known exploit signatures (Log4Shell-style payloads, etc.) |
| `AWSManagedRulesSQLiRuleSet` | SQL injection pattern blocking |
| `AWSManagedRulesAmazonIpReputationList` | Blocks traffic from IPs on AWS's threat-intel reputation list |
| Custom rate-based rule | Blocks any single IP exceeding 2,000 requests / 5 minutes (basic L7 DDoS/brute-force mitigation) |

WAF is set to **Count mode** in a new environment for the first 48 hours to validate against false positives on real traffic, then switched to **Block mode** — this staged rollout is a deliberate practice to avoid blocking legitimate users on day one.
