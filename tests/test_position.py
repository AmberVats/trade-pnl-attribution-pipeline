from src.position import calculate_positions


def test_calculate_positions():
    positions = calculate_positions()

    assert len(positions) == 4

    aapl_aug3 = next(
        row for row in positions
        if row["position_date"].isoformat() == "2026-08-03"
        and row["instrument_id"] == "AAPL"
    )

    assert aapl_aug3["quantity"] == 100
    assert aapl_aug3["market_price"] == 200
    assert aapl_aug3["market_value"] == 20000


def test_aapl_cumulative_position():
    positions = calculate_positions()

    aapl_aug4 = next(
        row for row in positions
        if row["position_date"].isoformat() == "2026-08-04"
        and row["instrument_id"] == "AAPL"
    )

    assert aapl_aug4["quantity"] == 75