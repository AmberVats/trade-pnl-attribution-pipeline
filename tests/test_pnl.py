from src.pnl import calculate_pnl


def test_calculate_pnl():
    pnl = calculate_pnl()

    assert len(pnl) == 4


def test_aapl_realized_pnl():
    pnl = calculate_pnl()

    aapl_aug4 = next(
        row for row in pnl
        if row["pnl_date"].isoformat() == "2026-08-04"
        and row["instrument_id"] == "AAPL"
    )

    assert aapl_aug4["realized_pnl"] == 125
    assert aapl_aug4["unrealized_pnl"] == 375
    assert aapl_aug4["total_pnl"] == 500