from sqlalchemy import text

from src.db import engine


def calculate_positions():
    """
    Calculate cumulative daily positions, average cost,
    market price, and market value.

    BUY:
        Increases position quantity and updates weighted average price.

    SELL:
        Decreases position quantity while keeping the existing
        average price of the remaining position.

    Market value:
        quantity * market price
    """

    with engine.begin() as connection:

        # ---------------------------------------------------------
        # 1. Clear previously calculated positions
        # ---------------------------------------------------------
        connection.execute(
            text("DELETE FROM fct_position")
        )

        # ---------------------------------------------------------
        # 2. Get all trades in chronological order
        # ---------------------------------------------------------
        trades_query = text(
            """
            SELECT
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

        # ---------------------------------------------------------
        # 3. Calculate running positions
        # ---------------------------------------------------------
        positions = {}

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

            # -----------------------------------------------------
            # BUY
            # -----------------------------------------------------
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

            # -----------------------------------------------------
            # SELL
            # -----------------------------------------------------
            elif trade["side"] == "SELL":

                current["quantity"] -= quantity

                # Average cost of remaining position does not
                # change when using weighted-average costing.

                if current["quantity"] == 0:
                    current["average_price"] = 0

            # -----------------------------------------------------
            # Get market price for this date
            # -----------------------------------------------------
            price_query = text(
                """
                SELECT close_price
                FROM fct_market_price
                WHERE price_date = :price_date
                  AND instrument_id = :instrument_id
                """
            )

            market_price = connection.execute(
                price_query,
                {
                    "price_date": trade["trade_date"],
                    "instrument_id": trade["instrument_id"]
                }
            ).scalar()

            # -----------------------------------------------------
            # Calculate market value
            # -----------------------------------------------------
            market_value = None

            if market_price is not None:
                market_value = (
                    current["quantity"] * market_price
                )

            # -----------------------------------------------------
            # Insert position snapshot
            # -----------------------------------------------------
            insert_query = text(
                """
                INSERT INTO fct_position (
                    position_date,
                    book,
                    instrument_id,
                    quantity,
                    average_price,
                    market_price,
                    market_value,
                    currency
                )
                VALUES (
                    :position_date,
                    :book,
                    :instrument_id,
                    :quantity,
                    :average_price,
                    :market_price,
                    :market_value,
                    :currency
                )
                """
            )

            connection.execute(
                insert_query,
                {
                    "position_date": trade["trade_date"],
                    "book": trade["book"],
                    "instrument_id": trade["instrument_id"],
                    "quantity": current["quantity"],
                    "average_price": current["average_price"],
                    "market_price": market_price,
                    "market_value": market_value,
                    "currency": current["currency"]
                }
            )

    # -------------------------------------------------------------
    # 4. Return calculated positions
    # -------------------------------------------------------------
    with engine.connect() as connection:

        result = connection.execute(
            text(
                """
                SELECT
                    position_date,
                    book,
                    instrument_id,
                    quantity,
                    average_price,
                    market_price,
                    market_value,
                    currency
                FROM fct_position
                ORDER BY
                    position_date,
                    book,
                    instrument_id
                """
            )
        )

        return [dict(row) for row in result.mappings().all()]