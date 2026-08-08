from src.attribution import calculate_attribution


def test_calculate_attribution():
    attribution = calculate_attribution()

    assert len(attribution) == 4


def test_aapl_attribution():
    attribution = calculate_attribution()

    aapl_aug4 = next(
        row for row in attribution
        if row["attribution_date"].isoformat() == "2026-08-04"
        and row["instrument_id"] == "AAPL"
    )

    assert aapl_aug4["trading_pnl"] == 125
    assert aapl_aug4["price_pnl"] == 375
    assert aapl_aug4["total_pnl"] == 500