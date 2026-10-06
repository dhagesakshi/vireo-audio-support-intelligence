import pandas as pd

LEGACY = "legacy_fd"
CURRENT = "helpdesk"

def reconcile_tickets(tickets: pd.DataFrame) -> pd.DataFrame:
    df = tickets.copy()

    for col in ["created_at", "first_response_at", "resolved_at"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # The export can contain the same legacy ticket twice: once from Freshdesk
    # and once after re-import into the current helpdesk. The current-helpdesk
    # copy is preferred because it contains the IST-normalized resolution
    # timestamp and current-system CSAT when available.
    priority = {LEGACY: 0, CURRENT: 1}
    df["_source_priority"] = df["source_system"].map(priority).fillna(-1)
    df = (
        df.sort_values(["ticket_id", "_source_priority"])
          .drop_duplicates("ticket_id", keep="last")
          .drop(columns="_source_priority")
          .copy()
    )

    # Legacy resolution timestamps were reconstructed from a UTC event log.
    # The export's displayed timestamps are IST, so normalize legacy-only
    # resolution timestamps by +05:30.
    legacy_mask = (
        df["source_system"].eq(LEGACY)
        & df["resolved_at"].notna()
    )
    df.loc[legacy_mask, "resolved_at"] += pd.Timedelta(hours=5, minutes=30)

    # Policy: legacy CSAT 0 means no response, not a score.
    df.loc[df["csat_score"].eq(0), "csat_score"] = pd.NA

    return df
