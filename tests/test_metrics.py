import pandas as pd
from src.metrics import add_repeat_proxy, calculate_business_case

def test_repeat_proxy():
    df = pd.DataFrame({
        "customer_id": ["C1", "C1"],
        "created_at": pd.to_datetime(["2026-01-01", "2026-01-10"]),
        "resolved_at": pd.to_datetime(["2026-01-02", "2026-01-11"]),
        "category": ["Connectivity", "Connectivity"],
        "product_sku": ["P1", "P1"],
    })
    out = add_repeat_proxy(df)
    assert out["repeat_contact_proxy"].iloc[1] is True

def test_business_case():
    df = pd.DataFrame({"repeat_contact_proxy": [True, False, False, False]})
    result = calculate_business_case(
        df,
        weekly_volume=100,
        target_rate=0.10,
        blended_cost=290,
        quarter_weeks=1,
    )
    assert result["current_repeat_rate"] == 0.25
    assert result["avoided_contacts_per_quarter"] == 15
    assert result["estimated_quarterly_savings_inr"] == 4350
