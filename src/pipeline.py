from sqlalchemy import text

from src.db import engine
from src.ingestion import (
    load_instruments,
    load_trades,
    load_market_prices,
)
from src.position import calculate_positions
from src.pnl import calculate_pnl
from src.attribution import calculate_attribution
from src.report import generate_report


def reset_input_tables():
    """Clear previously loaded input data."""

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                TRUNCATE TABLE
                    fct_trade,
                    fct_market_price,
                    dim_instrument
                RESTART IDENTITY CASCADE
                """
            )
        )


def run_pipeline():
    """Run the complete Trade PnL Attribution pipeline."""

    print("========================================")
    print("Trade PnL Attribution Pipeline")
    print("========================================")

    # -------------------------------------------------
    # Reset previous input data
    # -------------------------------------------------

    print("\nResetting previous input data...")

    reset_input_tables()

    print("Input tables cleared")

    # -------------------------------------------------
    # 1. Load instruments
    # -------------------------------------------------

    print("\n[1/6] Loading instruments...")

    instruments = load_instruments(
        "data/sample/instruments.csv"
    )

    print(f"Loaded {instruments} instruments")

    # -------------------------------------------------
    # 2. Load trades
    # -------------------------------------------------

    print("\n[2/6] Loading trades...")

    trades = load_trades(
        "data/sample/trades.csv"
    )

    print(f"Loaded {trades} trades")

    # -------------------------------------------------
    # 3. Load market prices
    # -------------------------------------------------

    print("\n[3/6] Loading market prices...")

    market_prices = load_market_prices(
        "data/sample/market_prices.csv"
    )

    print(f"Loaded {market_prices} market prices")

    # -------------------------------------------------
    # 4. Calculate positions
    # -------------------------------------------------

    print("\n[4/6] Calculating positions...")

    positions = calculate_positions()

    print(f"Calculated {len(positions)} positions")

    # -------------------------------------------------
    # 5. Calculate PnL and attribution
    # -------------------------------------------------

    print("\n[5/6] Calculating PnL and attribution...")

    pnl = calculate_pnl()

    print(f"Calculated {len(pnl)} PnL records")

    attribution = calculate_attribution()

    print(
        f"Calculated {len(attribution)} attribution records"
    )

    # -------------------------------------------------
    # 6. Generate HTML report
    # -------------------------------------------------

    print("\n[6/6] Generating HTML report...")

    report_file = generate_report()

    print(f"Report generated: {report_file}")

    # -------------------------------------------------
    # Pipeline completed
    # -------------------------------------------------

    print("\n========================================")
    print("Pipeline completed successfully")
    print("========================================")

    return {
        "instruments": instruments,
        "trades": trades,
        "market_prices": market_prices,
        "positions": positions,
        "pnl": pnl,
        "attribution": attribution,
        "report": report_file,
    }


if __name__ == "__main__":
    run_pipeline()