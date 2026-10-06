import json
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"

# Sparse weeks below this ticket count are excluded from the
# default executive view. Underlying data is not changed.
SPARSE_WEEK_THRESHOLD = 10


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Vireo Audio Support Intelligence",
    page_icon="🎧",
    layout="wide",
)


# ============================================================
# HEADER
# ============================================================

st.title("Vireo Audio — Support Intelligence")

st.caption(
    "Weekly support digest, complaint trends and Tier-1 workload view"
)


# ============================================================
# REQUIRED OUTPUT FILES
# ============================================================

required = [
    OUT / "ticket_classifications.csv",
    OUT / "weekly_complaints.csv",
    OUT / "leaderboard.csv",
    OUT / "business_metrics.json",
]

missing = [p.name for p in required if not p.exists()]

if missing:
    st.error(
        "Run `python -m src.pipeline` first. Missing: "
        + ", ".join(missing)
    )
    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

tickets = pd.read_csv(
    OUT / "ticket_classifications.csv",
    parse_dates=[
        "created_at",
        "week_start",
        "resolve_week",
    ],
)

weekly = pd.read_csv(
    OUT / "weekly_complaints.csv",
    parse_dates=["week_start"],
)

leaderboard = pd.read_csv(
    OUT / "leaderboard.csv",
    parse_dates=["resolve_week"],
)

metrics = json.loads(
    (OUT / "business_metrics.json").read_text(
        encoding="utf-8"
    )
)


# ============================================================
# TOP KPI CARDS
# ============================================================

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "Canonical tickets",
    f"{len(tickets):,}",
)

m2.metric(
    "Repeat-contact proxy",
    f"{metrics['current_repeat_rate']:.1%}",
)

m3.metric(
    "Target",
    f"{metrics['target_repeat_rate']:.1%}",
)

m4.metric(
    "Quarterly opportunity",
    f"₹{metrics['estimated_quarterly_savings_inr']:,.0f}",
)


# ============================================================
# EXECUTIVE TAKEAWAY
# ============================================================

st.subheader("Executive takeaway")

current_rate = metrics["current_repeat_rate"]
target_rate = metrics["target_repeat_rate"]
savings = metrics["estimated_quarterly_savings_inr"]

st.info(
    f"The repeat-contact rate is {current_rate:.1%} versus the "
    f"{target_rate:.1%} target. The estimated opportunity is "
    f"₹{savings:,.0f} per quarter if the rate reaches the target "
    f"at the configured weekly volume and blended contact cost. "
    f"This is an estimate, not a guaranteed saving."
)


# ============================================================
# DATA QUALITY & COVERAGE
# ============================================================

st.subheader("Data quality & coverage")

total_tickets = len(tickets)

missing_category = int(
    tickets["category"].isna().sum()
)

missing_customer_message = int(
    tickets["customer_message"].isna().sum()
)

if "ticket_id" in tickets.columns:
    duplicate_ticket_ids = int(
        tickets["ticket_id"].duplicated().sum()
    )
else:
    duplicate_ticket_ids = 0

date_min = tickets["created_at"].min()
date_max = tickets["created_at"].max()

q1, q2, q3, q4 = st.columns(4)

q1.metric(
    "Tickets processed",
    f"{total_tickets:,}",
)

q2.metric(
    "Missing categories",
    f"{missing_category:,}",
)

q3.metric(
    "Missing messages",
    f"{missing_customer_message:,}",
)

q4.metric(
    "Duplicate ticket IDs",
    f"{duplicate_ticket_ids:,}",
)

st.caption(
    f"Coverage: {date_min:%d %b %Y} to {date_max:%d %b %Y}. "
    "Metrics are calculated from the reconciled ticket dataset."
)


# ============================================================
# LATEST COMPLAINT MIX
# ============================================================

st.subheader("Latest weekly complaint mix")

# Count tickets per week.
weekly_ticket_counts = (
    tickets.groupby("week_start")
    .size()
    .sort_index()
)

# Ignore very sparse trailing weeks in the default executive view.
meaningful_weeks = weekly_ticket_counts[
    weekly_ticket_counts >= SPARSE_WEEK_THRESHOLD
].index

if len(meaningful_weeks) > 0:
    latest_week = meaningful_weeks.max()
else:
    latest_week = weekly_ticket_counts.index.max()

latest = tickets[
    tickets["week_start"] == latest_week
].copy()

st.markdown(
    f"**Complaint categories — week of "
    f"{latest_week:%Y-%m-%d}** "
    f"({len(latest):,} tickets)"
)

st.caption(
    f"Default view excludes weeks with fewer than "
    f"{SPARSE_WEEK_THRESHOLD} tickets to avoid presenting "
    "a low-signal or potentially incomplete trailing week "
    "as the main weekly signal."
)

mix = (
    latest["category"]
    .value_counts()
    .rename_axis("category")
    .reset_index(name="tickets")
)

fig_mix = px.bar(
    mix,
    x="tickets",
    y="category",
    orientation="h",
    title="Complaint volume by category",
)

fig_mix.update_layout(
    yaxis_title="Complaint category",
    xaxis_title="Tickets",
)

st.plotly_chart(
    fig_mix,
    use_container_width=True,
)


# ============================================================
# WEEKLY COMPLAINT TREND
# ============================================================

st.subheader("Weekly complaint trend")

trend = (
    weekly
    .pivot(
        index="week_start",
        columns="category",
        values="share",
    )
    .fillna(0)
)

st.line_chart(trend)


# ============================================================
# TIER-1 WORKLOAD LEADERBOARD
# ============================================================

st.subheader("Tier-1 workload leaderboard")

st.caption(
    "Ticket-volume view only. This is not a measure of overall "
    "agent performance or quality."
)

# Count closed tickets per week.
leaderboard_weekly_counts = (
    leaderboard.groupby("resolve_week")["tickets_closed"]
    .sum()
    .sort_index()
)

# Exclude sparse trailing weeks from the default leaderboard view.
meaningful_lb_weeks = leaderboard_weekly_counts[
    leaderboard_weekly_counts >= SPARSE_WEEK_THRESHOLD
].index

if len(meaningful_lb_weeks) > 0:
    lb_week = meaningful_lb_weeks.max()
else:
    lb_week = leaderboard_weekly_counts.index.max()

lb = leaderboard[
    leaderboard["resolve_week"] == lb_week
].copy()

lb = lb.sort_values(
    "tickets_closed",
    ascending=False,
)

st.markdown(
    f"**Week of {lb_week:%Y-%m-%d}**"
)

st.caption(
    f"Default leaderboard excludes weeks with fewer than "
    f"{SPARSE_WEEK_THRESHOLD} closed tickets."
)

st.dataframe(
    lb,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# MODEL VALIDATION
# ============================================================

st.subheader("Model validation")

sample_size = metrics[
    "sample_size"
] if "sample_size" in metrics else None

accuracy = metrics[
    "accuracy_against_intake_labels"
]

macro_f1 = metrics[
    "macro_f1_against_intake_labels"
]

if sample_size is not None:

    st.write(
        f"Holdout sample: **{sample_size:,} tickets**. "
        f"Agreement with exported intake labels: "
        f"**{accuracy:.1%}** "
        f"(macro-F1 **{macro_f1:.3f}**)."
    )

else:

    st.write(
        f"Agreement with exported intake labels: "
        f"**{accuracy:.1%}** "
        f"(macro-F1 **{macro_f1:.3f}**)."
    )

st.warning(
    "This validates agreement with the source intake labels, "
    "not independent human ground truth."
)


# ============================================================
# METHOD AND LIMITATIONS
# ============================================================

st.subheader("Method and limitations")

with st.expander("How this works"):

    st.markdown(
        """
**Classification**

A local text classifier is trained against the exported
intake category labels. The model is evaluated on a held-out
test sample before being applied to the full ticket dataset.

**Weekly digest**

Complaint volumes and category shares are calculated
deterministically from the processed ticket data.

**Repeat-contact proxy**

The repeat-contact metric identifies subsequent contacts
within the configured window for the same customer, category
and product.

**Business opportunity**

The estimated opportunity represents the contact-cost savings
if the repeat-contact proxy reaches the configured target.
It is an estimate rather than a guaranteed financial outcome.

**Leaderboard**

The leaderboard shows ticket volume closed by agent per week.
It should be interpreted as a workload indicator, not as a
standalone performance ranking.

**Sparse-week handling**

Weeks with fewer than the configured threshold of tickets are
excluded from the default executive and leaderboard views.
The underlying ticket data remains unchanged.
"""
    )


# ============================================================
# DATA NOTE
# ============================================================

st.subheader("Data note")

st.write(
    """
The dashboard uses the reconciled ticket dataset produced by
the pipeline. Source intake labels are treated as reference
labels for model agreement testing; they are not assumed to be
perfect human ground truth.
"""
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Vireo Audio Support Intelligence • AI-assisted analysis "
    "with deterministic business metrics"
)