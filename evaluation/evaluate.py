from pathlib import Path
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, classification_report

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "outputs/ticket_classifications.csv")

mask = df["model_category"].notna() & df["category"].notna()

print("Sample:", mask.sum())
print("Accuracy:", accuracy_score(df.loc[mask, "category"], df.loc[mask, "model_category"]))
print("Macro F1:", f1_score(
    df.loc[mask, "category"],
    df.loc[mask, "model_category"],
    average="macro"
))
print(classification_report(
    df.loc[mask, "category"],
    df.loc[mask, "model_category"],
    zero_division=0
))
