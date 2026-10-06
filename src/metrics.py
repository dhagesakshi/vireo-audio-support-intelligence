import pandas as pd
import numpy as np

CHANNEL_COST = {
    "chat": 210,
    "email": 260,
    "voice": 520,
    "social": 240,
}

FIRST_RESPONSE_TARGET = {
    "chat": 15,
    "voice": 120,
    "social": 240,
    "email": 480,
}

def add_operational_metrics(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    out["first_response_min"] = (
        out["first_response_at"] - out["created_at"]
    ).dt.total_seconds() / 60

    out["sla_target_min"] = out["channel"].map(FIRST_RESPONSE_TARGET)
    out["sla_breach"] = out["first_response_min"] > out["sla_target_min"]

    out["attendance"] = out["status"].isin(["resolved", "closed"])

    out["contact_cost_inr"] = out["channel"].map(CHANNEL_COST)

    out["week_start"] = (
        out["created_at"]
        .dt.to_period("W-SUN")
        .dt.start_time
    )

    out["resolve_week"] = (
        out["resolved_at"]
        .dt.to_period("W-SUN")
        .dt.start_time
    )

    return out

def add_repeat_proxy(df: pd.DataFrame, window_days=30) -> pd.DataFrame:
    out = df.sort_values(["customer_id", "created_at"]).copy()

    out["previous_resolution"] = out.groupby("customer_id")["resolved_at"].shift()
    out["previous_category"] = out.groupby("customer_id")["category"].shift()
    out["previous_product"] = out.groupby("customer_id")["product_sku"].shift()

    gap = (
        out["created_at"] - out["previous_resolution"]
    ).dt.total_seconds()

    out["repeat_contact_proxy"] = (
        gap.between(0, window_days * 86400, inclusive="both")
        & out["category"].eq(out["previous_category"])
        & out["product_sku"].eq(out["previous_product"])
    )

    return out

def calculate_business_case(df: pd.DataFrame, weekly_volume=650,
                            target_rate=0.08, blended_cost=290,
                            quarter_weeks=13):
    current_rate = float(df["repeat_contact_proxy"].mean())
    quarterly_tickets = weekly_volume * quarter_weeks
    avoided_contacts = quarterly_tickets * max(current_rate - target_rate, 0)
    quarterly_savings = avoided_contacts * blended_cost

    return {
        "current_repeat_rate": current_rate,
        "target_repeat_rate": target_rate,
        "quarterly_tickets_at_current_volume": quarterly_tickets,
        "avoided_contacts_per_quarter": avoided_contacts,
        "estimated_quarterly_savings_inr": quarterly_savings,
    }
