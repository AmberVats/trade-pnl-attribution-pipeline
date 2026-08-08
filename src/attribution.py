from sqlalchemy import text

from src.db import engine


def calculate_attribution():
    """
    Populate the PnL attribution table.

    The first attribution layer uses the existing PnL calculation:

    realized_pnl   -> trading/realized contribution
    unrealized_pnl -> price contribution
    total_pnl      -> realized + unrealized
    """

    with engine.begin() as connection:

        # Clear previously calculated attribution
        connection.execute(
            text("DELETE FROM fct_pnl_attribution")
        )

        query = text(
            """
            SELECT
                pnl_date,
                book,
                instrument_id,
                realized_pnl,
                unrealized_pnl,
                total_pnl,
                currency
            FROM fct_pnl
            ORDER BY
                pnl_date,
                book,
                instrument_id
            """
        )

        rows = connection.execute(
            query
        ).mappings().all()

        insert_query = text(
            """
            INSERT INTO fct_pnl_attribution (
                attribution_date,
                book,
                instrument_id,
                trading_pnl,
                price_pnl,
                realized_pnl,
                unrealized_pnl,
                total_pnl,
                currency
            )
            VALUES (
                :attribution_date,
                :book,
                :instrument_id,
                :trading_pnl,
                :price_pnl,
                :realized_pnl,
                :unrealized_pnl,
                :total_pnl,
                :currency
            )
            """
        )

        for row in rows:

            realized_pnl = row["realized_pnl"]
            unrealized_pnl = row["unrealized_pnl"]

            # Trading contribution is the realized component.
            trading_pnl = realized_pnl

            # Price contribution is the unrealized component.
            price_pnl = unrealized_pnl

            connection.execute(
                insert_query,
                {
                    "attribution_date": row["pnl_date"],
                    "book": row["book"],
                    "instrument_id": row["instrument_id"],
                    "trading_pnl": trading_pnl,
                    "price_pnl": price_pnl,
                    "realized_pnl": realized_pnl,
                    "unrealized_pnl": unrealized_pnl,
                    "total_pnl": row["total_pnl"],
                    "currency": row["currency"],
                },
            )

    # Return the calculated attribution
    with engine.connect() as connection:

        result = connection.execute(
            text(
                """
                SELECT
                    attribution_date,
                    book,
                    instrument_id,
                    trading_pnl,
                    price_pnl,
                    realized_pnl,
                    unrealized_pnl,
                    total_pnl,
                    currency
                FROM fct_pnl_attribution
                ORDER BY
                    attribution_date,
                    book,
                    instrument_id
                """
            )
        )

        return [
            dict(row)
            for row in result.mappings().all()
        ]