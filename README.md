# Vireo Audio — Support Intelligence

A lightweight, reproducible AI/ML-assisted analysis tool for Vireo Audio support tickets.

The tool turns support-ticket data into:
- weekly complaint trends,
- a repeat-contact proxy,
- a workload-focused Tier-1 leaderboard,
- model validation metrics,
- and an estimated financial opportunity from reducing repeat contacts.

---

## Business objective

Vireo Audio receives a large volume of support tickets across its customer-support operation.

The goal is to reduce the manual effort required to understand recurring complaints and give CX leadership a repeatable weekly view of:

1. What customers are complaining about.
2. Whether repeat contacts are a significant operational issue.
3. How many tickets agents are closing each week.
4. What financial opportunity exists if repeat contacts are reduced.

The current processed dataset contains **11,875 canonical tickets**.

The current repeat-contact proxy is approximately **10.2%**, versus the configured target of **8%**.

At the configured weekly volume and blended contact cost, reaching the target represents an estimated opportunity of approximately **₹55,098 per quarter**.

This is an estimate of avoidable contact cost, not a guaranteed realized saving.

---

## What it does

The pipeline:

1. Reconciles duplicated legacy/current ticket IDs.
2. Normalizes ticket and resolution timestamps.
3. Calculates operational metrics such as SLA breaches and contact cost.
4. Calculates a repeat-contact proxy using the configured repeat window.
5. Builds weekly complaint-volume and category-share tables.
6. Trains a local TF-IDF + Logistic Regression text classifier.
7. Evaluates the classifier on a stratified holdout sample.
8. Generates a Tier-1 ticket-volume workload leaderboard.
9. Produces business metrics and a weekly digest.
10. Exposes the results through a Streamlit dashboard.

---

## Architecture

```text
Input CSV files
      |
      v
Data loading
      |
      v
Ticket reconciliation
      |
      v
Operational metrics
      |
      +----------------------+
      |                      |
      v                      v
Repeat-contact proxy     Text classifier
      |                      |
      |                      v
      |                 Holdout evaluation
      |                      |
      +----------+-----------+
                 |
                 v
          Weekly aggregation
                 |
        +--------+---------+
        |        |         |
        v        v         v
      Digest  Leaderboard  Business metrics
        |        |         |
        +--------+---------+
                 |
                 v
        Streamlit dashboard