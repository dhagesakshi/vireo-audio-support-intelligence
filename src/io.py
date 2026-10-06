from pathlib import Path
import pandas as pd

REQUIRED = ["tickets.csv", "agents.csv", "orders.csv", "products.csv", "customers.csv"]

def load_csvs(data_dir: Path):
    missing = [f for f in REQUIRED if not (data_dir / f).exists()]
    if missing:
        raise FileNotFoundError(
            "Missing required data files: " + ", ".join(missing)
        )

    return {
        "tickets": pd.read_csv(data_dir / "tickets.csv"),
        "agents": pd.read_csv(data_dir / "agents.csv"),
        "orders": pd.read_csv(data_dir / "orders.csv"),
        "products": pd.read_csv(data_dir / "products.csv"),
        "customers": pd.read_csv(data_dir / "customers.csv"),
    }
