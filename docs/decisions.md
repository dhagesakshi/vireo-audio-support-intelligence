# Key decisions

## 1. Duplicate reconciliation
The export contains repeated ticket IDs under `legacy_fd` and `helpdesk`. The current-helpdesk copy is retained for duplicate IDs because the policy says the current system re-imported legacy tickets and the legacy resolution timestamp comes from a UTC event log.

## 2. Legacy timestamp normalization
Legacy resolution timestamps are shifted +05:30 before calculating handle time/repeat contacts. Without this, many legacy tickets appear to resolve before they were created.

## 3. Repeat-contact definition
The exact policy definition requires the same issue. The export has no canonical issue ID, so the tool uses a transparent proxy:
same customer + same product + same intake category + new contact within 30 days after prior resolution.

This is explicitly called a proxy, not exact FCR.

## 4. Agent leaderboard
The requested leaderboard is retained, but it is a workload/volume view. Escalations & Warranty is excluded because policy says Tier-2 cases are measured in days, not weekly ticket volume.

## 5. AI scope
The runtime uses a local TF-IDF + logistic-regression text classifier so the tool works without an API key. An optional LLM layer can be added for narrative summarization, but financial calculations and KPI aggregation remain deterministic.
