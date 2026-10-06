from pathlib import Path
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

from .config import DATA_DIR, OUTPUT_DIR, load_policy
from .io import load_csvs
from .reconcile import reconcile_tickets
from .metrics import add_operational_metrics, add_repeat_proxy, calculate_business_case
from .text_model import train_model, predict_with_confidence

def top_terms(texts, n=8):
    from sklearn.feature_extraction.text import TfidfVectorizer
    import numpy as np

    clean = (
        pd.Series(texts)
        .fillna("")
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.lower()
    )
    stop = [
        "the","and","for","with","this","that","have","your","from",
        "you","are","was","were","to","of","in","on","is","it","i",
        "my","me","a","an","or","but","not","can","will","would",
        "could","has","had","be","been","as","at","by","we","they",
        "them","our","their","please","hello","hi","dear","thanks"
    ]

    vec = TfidfVectorizer(
        stop_words=stop,
        ngram_range=(1,2),
        min_df=4,
        max_features=3000,
        sublinear_tf=True
    )
    X = vec.fit_transform(clean)
    scores = X.mean(axis=0).A1
    terms = vec.get_feature_names_out()
    return terms[scores.argsort()[::-1][:n]].tolist()

def run():
    OUTPUT_DIR.mkdir(exist_ok=True)

    raw = load_csvs(DATA_DIR)
    tickets = reconcile_tickets(raw["tickets"])
    tickets = add_operational_metrics(tickets)
    tickets = add_repeat_proxy(tickets, load_policy()["repeat_window_days"])

    # Train/evaluate the local text classifier against the existing intake
    # category field. This is an agreement test against source labels, not
    # a claim that those labels are perfect ground truth.
    model_data = tickets[
        tickets["customer_message"].fillna("").str.strip().ne("")
    ].copy()

    train, test = train_test_split(
        model_data,
        test_size=0.20,
        random_state=42,
        stratify=model_data["category"]
    )

    model = train_model(train)
    pred, confidence = predict_with_confidence(
        model,
        test["customer_message"].fillna("").astype(str)
    )

    eval_result = {
        "sample_size": len(test),
        "accuracy_against_intake_labels": float(accuracy_score(test["category"], pred)),
        "macro_f1_against_intake_labels": float(
            f1_score(test["category"], pred, average="macro")
        ),
        "note": "This is agreement with the exported intake labels, not independent human ground truth."
    }

    # Predict category + confidence for every ticket.
    pred_all, conf_all = predict_with_confidence(
        model,
        tickets["customer_message"].fillna("").astype(str)
    )
    tickets["model_category"] = pred_all
    tickets["model_confidence"] = conf_all

    # Weekly digest tables.
    weekly = (
        tickets.groupby(["week_start", "category"])
        .size()
        .rename("tickets")
        .reset_index()
    )
    weekly["share"] = weekly.groupby("week_start")["tickets"].transform(
        lambda s: s / s.sum()
    )

    leaderboard = (
    tickets[
        tickets["attendance"]
    ]
    .groupby(["resolve_week", "agent_id"])
    .size()
    .rename("tickets_closed")
    .reset_index()
    .sort_values(
        ["resolve_week", "tickets_closed"],
        ascending=[True, False]
    )
)

    business = calculate_business_case(
        tickets,
        weekly_volume=load_policy()["weekly_current_volume"],
        target_rate=load_policy()["target_repeat_rate"],
        blended_cost=load_policy()["cost_per_contact_inr"]["blended"],
        quarter_weeks=load_policy()["quarter_weeks"],
    )

    # Add high-level trend data for the latest complete week.
    max_date = tickets["created_at"].max()
    latest_full_week = (
        max_date.to_period("W-SUN").start_time
        if max_date.weekday() == 6
        else (max_date.to_period("W-SUN").start_time - pd.Timedelta(days=7))
    )

    latest = tickets[tickets["week_start"] == latest_full_week]
    latest_prev = tickets[
        tickets["week_start"] == latest_full_week - pd.Timedelta(days=7)
    ]

    def mix(df):
        return (df["category"].value_counts(normalize=True) * 100).round(2).to_dict()

    digest = {
        "latest_full_week": str(latest_full_week.date()),
        "ticket_count": int(len(latest)),
        "category_mix_pct": mix(latest),
        "previous_week_mix_pct": mix(latest_prev),
        "repeat_rate": float(latest["repeat_contact_proxy"].mean()) if len(latest) else None,
        "top_text_terms": top_terms(latest["customer_message"], 12) if len(latest) else [],
        "business_case": business,
        "evaluation": eval_result,
    }

    tickets.to_csv(OUTPUT_DIR / "ticket_classifications.csv", index=False)
    weekly.to_csv(OUTPUT_DIR / "weekly_complaints.csv", index=False)
    leaderboard.to_csv(OUTPUT_DIR / "leaderboard.csv", index=False)

    with open(OUTPUT_DIR / "business_metrics.json", "w", encoding="utf-8") as f:
        json.dump(business | eval_result, f, indent=2)

    with open(OUTPUT_DIR / "weekly_digest.json", "w", encoding="utf-8") as f:
        json.dump(digest, f, indent=2, default=str)

    print(json.dumps({
        "canonical_tickets": len(tickets),
        "repeat_rate": business["current_repeat_rate"],
        "quarterly_savings_at_8pct_target_inr": business["estimated_quarterly_savings_inr"],
        "classifier_accuracy_vs_intake_labels": eval_result["accuracy_against_intake_labels"],
        "classifier_macro_f1_vs_intake_labels": eval_result["macro_f1_against_intake_labels"],
    }, indent=2))

if __name__ == "__main__":
    run()
