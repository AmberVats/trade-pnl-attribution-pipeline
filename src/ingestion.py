from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.db import engine


def load_instruments(file_path: str | Path) -> int:
    """Load instrument master data into dim_instrument."""
    df = pd.read_csv(file_path)

    required_columns = {
        "instrument_id",
        "symbol",
        "instrument_type",
        "currency",
        "exchange",
        "sector",
        "active",
    }

    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing instrument columns: {sorted(missing)}")

    records = df.to_dict(orient="records")

    sql = text(
        """
        INSERT INTO dim_instrument (
            instrument_id,
            symbol,
            instrument_type,
            currency,
            exchange,
            sector,
            active
        )
        VALUES (
            :instrument_id,
            :symbol,
            :instrument_type,
            :currency,
            :exchange,
            :sector,
            :active
        )
        ON CONFLICT (instrument_id) DO UPDATE SET
            symbol = EXCLUDED.symbol,
            instrument_type = EXCLUDED.instrument_type,
            currency = EXCLUDED.currency,
            exchange = EXCLUDED.exchange,
            sector = EXCLUDED.sector,
            active = EXCLUDED.active
        """
    )

    with engine.begin() as connection:
        connection.execute(sql, records)

    return len(records)


def load_trades(file_path: str | Path) -> int:
    """Load trades into fct_trade."""
    df = pd.read_csv(file_path)

    required_columns = {
        "trade_date",
        "book",
        "instrument_id",
        "side",
        "quantity",
        "price",
        "currency",
        "trader",
    }

    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing trade columns: {sorted(missing)}")

    records = df.to_dict(orient="records")

    sql = text(
        """
        INSERT INTO fct_trade (
            trade_date,
            book,
            instrument_id,
            side,
            quantity,
            price,
            currency,
            trader
        )
        VALUES (
            :trade_date,
            :book,
            :instrument_id,
            :side,
            :quantity,
            :price,
            :currency,
            :trader
        )
        """
    )

    with engine.begin() as connection:
        connection.execute(sql, records)

    return len(records)


def load_market_prices(file_path: str | Path) -> int:
    """Load market prices into fct_market_price."""
    df = pd.read_csv(file_path)

    required_columns = {
        "price_date",
        "instrument_id",
        "close_price",
        "currency",
        "source",
    }

    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing market price columns: {sorted(missing)}")

    records = df.to_dict(orient="records")

    sql = text(
        """
        INSERT INTO fct_market_price (
            price_date,
            instrument_id,
            close_price,
            currency,
            source
        )
        VALUES (
            :price_date,
            :instrument_id,
            :close_price,
            :currency,
            :source
        )
        ON CONFLICT (price_date, instrument_id) DO UPDATE SET
            close_price = EXCLUDED.close_price,
            currency = EXCLUDED.currency,
            source = EXCLUDED.source
        """
    )

    with engine.begin() as connection:
        connection.execute(sql, records)

    return len(records)