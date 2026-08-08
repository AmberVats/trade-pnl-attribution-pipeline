from sqlalchemy import text

from src.db import engine


def calculate_pnl():
    """
    Calculate realized, unrealized, and total PnL
    using weighted-average cost.

    Realized PnL:
        SELL quantity * (sell price - average cost)

    Unrealized PnL:
        Closing position quantity *
        (market price - average cost)

    Total PnL:
        Realized PnL + Unrealized PnL
    """

    with engine.begin() as connection:

        # Clear previously calculated PnL
        connection.execute(
            text("DELETE FROM fct_pnl")
        )

        # Get trades in chronological order
        trades_query = text(
            """
            SELECT
                trade_id,
                trade_date,
                book,
                instrument_id,
                side,
                quantity,
                price,
                currency
            FROM fct_trade
            ORDER BY
                trade_date,
                trade_id
            """
        )

        trades = connection.execute(
            trades_query
        ).mappings().all()

        # Track average cost and quantity
        positions = {}

        # Track realized PnL by date/book/instrument
        daily_realized = {}

        for trade in trades:

            key = (
                trade["book"],
                trade["instrument_id"]
            )

            if key not in positions:
                positions[key] = {
                    "quantity": 0,
                    "average_price": 0,
                    "currency": trade["currency"]
                }

            current = positions[key]

            quantity = trade["quantity"]
            price = trade["price"]

            pnl_key = (
                trade["trade_date"],
                trade["book"],
                trade["instrument_id"]
            )

            if pnl_key not in daily_realized:
                daily_realized[pnl_key] = 0

            # -------------------------------------------------
            # BUY
            # -------------------------------------------------
            if trade["side"] == "BUY":

                old_quantity = current["quantity"]
                old_average = current["average_price"]

                new_quantity = old_quantity + quantity

                if new_quantity != 0:
                    new_average = (
                        (old_quantity * old_average)
                        + (quantity * price)
                    ) / new_quantity
                else:
                    new_average = 0

                current["quantity"] = new_quantity
                current["average_price"] = new_average

            # -------------------------------------------------
            # SELL
            # -------------------------------------------------
            elif trade["side"] == "SELL":

                realized_pnl = (
                    quantity
                    * (price - current["average_price"])
                )

                daily_realized[pnl_key] += realized_pnl

                current["quantity"] -= quantity

                if current["quantity"] == 0:
                    current["average_price"] = 0

        # -----------------------------------------------------
        # Calculate PnL from position snapshots
        # -----------------------------------------------------

        positions_query = text(
            """
            SELECT
                position_date,
                book,
                instrument_id,
                quantity,
                average_price,
                market_price,
                currency
            FROM fct_position
            ORDER BY
                position_date,
                book,
                instrument_id
            """
        )

        position_rows = connection.execute(
            positions_query
        ).mappings().all()

        # Track previous market price and quantity
        previous_positions = {}

        insert_query = text(
            """
            INSERT INTO fct_pnl (
                pnl_date,
                book,
                instrument_id,
                realized_pnl,
                unrealized_pnl,
                total_pnl,
                currency
            )
            VALUES (
                :pnl_date,
                :book,
                :instrument_id,
                :realized_pnl,
                :unrealized_pnl,
                :total_pnl,
                :currency
            )
            """
        )

        for position in position_rows:

            key = (
                position["book"],
                position["instrument_id"]
            )

            realized_pnl = daily_realized.get(
                (
                    position["position_date"],
                    position["book"],
                    position["instrument_id"]
                ),
                0
            )

            # Unrealized PnL is based on current position
            # and the difference between market price
            # and average cost.
            unrealized_pnl = (
                position["quantity"]
                * (
                    position["market_price"]
                    - position["average_price"]
                )
            )

            total_pnl = (
                realized_pnl
                + unrealized_pnl
            )

            connection.execute(
                insert_query,
                {
                    "pnl_date": position["position_date"],
                    "book": position["book"],
                    "instrument_id": position["instrument_id"],
                    "realized_pnl": realized_pnl,
                    "unrealized_pnl": unrealized_pnl,
                    "total_pnl": total_pnl,
                    "currency": position["currency"]
                }
            )

    # ---------------------------------------------------------
    # Return calculated PnL
    # ---------------------------------------------------------

    with engine.connect() as connection:

        result = connection.execute(
            text(
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
        )

        return [
            dict(row)
            for row in result.mappings().all()
        ]