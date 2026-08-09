from pathlib import Path
from datetime import datetime

from sqlalchemy import text

from src.db import engine


REPORT_DIR = Path("reports")
REPORT_FILE = REPORT_DIR / "pnl_report.html"


def _money(value):
    if value is None:
        return "$0.00"
    return f"${float(value):,.2f}"


def _number(value):
    if value is None:
        return "0"
    return f"{float(value):,.2f}"


def _table_rows(rows, columns):
    html = ""

    for row in rows:
        html += "<tr>"

        for column in columns:
            value = row[column]

            if column in {
                "trading_pnl",
                "price_pnl",
                "realized_pnl",
                "unrealized_pnl",
                "total_pnl",
                "market_value",
            }:
                value = _money(value)

            html += f"<td>{value}</td>"

        html += "</tr>"

    return html


def generate_report():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with engine.connect() as connection:

        # -------------------------------------------------
        # Daily PnL
        # -------------------------------------------------

        daily_query = text(
            """
            SELECT
                attribution_date,
                book,
                trading_pnl,
                price_pnl,
                realized_pnl,
                unrealized_pnl,
                total_pnl,
                currency
            FROM vw_daily_book_pnl
            ORDER BY attribution_date, book
            """
        )

        daily_rows = connection.execute(
            daily_query
        ).mappings().all()

        # -------------------------------------------------
        # Instrument PnL
        # -------------------------------------------------

        instrument_query = text(
            """
            SELECT
                instrument_id,
                book,
                trading_pnl,
                price_pnl,
                realized_pnl,
                unrealized_pnl,
                total_pnl,
                currency
            FROM vw_instrument_pnl
            ORDER BY total_pnl DESC, instrument_id
            """
        )

        instrument_rows = connection.execute(
            instrument_query
        ).mappings().all()

        # -------------------------------------------------
        # Attribution
        # -------------------------------------------------

        attribution_query = text(
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
            FROM vw_daily_pnl_attribution
            ORDER BY attribution_date, instrument_id
            """
        )

        attribution_rows = connection.execute(
            attribution_query
        ).mappings().all()

        # -------------------------------------------------
        # Positions
        # -------------------------------------------------

        position_query = text(
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
            ORDER BY position_date, instrument_id
            """
        )

        position_rows = connection.execute(
            position_query
        ).mappings().all()

    # -----------------------------------------------------
    # Summary calculations
    # -----------------------------------------------------

    total_pnl = sum(
        float(row["total_pnl"] or 0)
        for row in instrument_rows
    )

    realized_pnl = sum(
        float(row["realized_pnl"] or 0)
        for row in instrument_rows
    )

    unrealized_pnl = sum(
        float(row["unrealized_pnl"] or 0)
        for row in instrument_rows
    )

    trading_pnl = sum(
        float(row["trading_pnl"] or 0)
        for row in instrument_rows
    )

    price_pnl = sum(
        float(row["price_pnl"] or 0)
        for row in instrument_rows
    )

    currencies = sorted(
        {
            row["currency"]
            for row in instrument_rows
            if row["currency"]
        }
    )

    currency = currencies[0] if currencies else "USD"

    generated_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # -----------------------------------------------------
    # Daily PnL table
    # -----------------------------------------------------

    daily_html = _table_rows(
        daily_rows,
        [
            "attribution_date",
            "book",
            "trading_pnl",
            "price_pnl",
            "realized_pnl",
            "unrealized_pnl",
            "total_pnl",
            "currency",
        ],
    )

    # -----------------------------------------------------
    # Instrument table
    # -----------------------------------------------------

    instrument_html = _table_rows(
        instrument_rows,
        [
            "instrument_id",
            "book",
            "trading_pnl",
            "price_pnl",
            "realized_pnl",
            "unrealized_pnl",
            "total_pnl",
            "currency",
        ],
    )

    # -----------------------------------------------------
    # Attribution table
    # -----------------------------------------------------

    attribution_html = _table_rows(
        attribution_rows,
        [
            "attribution_date",
            "book",
            "instrument_id",
            "trading_pnl",
            "price_pnl",
            "realized_pnl",
            "unrealized_pnl",
            "total_pnl",
            "currency",
        ],
    )

    # -----------------------------------------------------
    # Position table
    # -----------------------------------------------------

    position_html = ""

    for row in position_rows:
        position_html += "<tr>"

        position_html += f"<td>{row['position_date']}</td>"
        position_html += f"<td>{row['book']}</td>"
        position_html += f"<td>{row['instrument_id']}</td>"
        position_html += f"<td>{_number(row['quantity'])}</td>"
        position_html += f"<td>{_money(row['average_price'])}</td>"
        position_html += f"<td>{_money(row['market_price'])}</td>"
        position_html += f"<td>{_money(row['market_value'])}</td>"
        position_html += f"<td>{row['currency']}</td>"

        position_html += "</tr>"

    # -----------------------------------------------------
    # HTML document
    # -----------------------------------------------------

    html = f"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>Trade PnL Attribution Report</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Arial,
        sans-serif;

    background: #f4f6f8;
    color: #1f2937;
}}

.container {{
    max-width: 1400px;
    margin: auto;
    padding: 30px;
}}

.header {{
    background: #111827;
    color: white;
    padding: 30px;
    border-radius: 12px;
    margin-bottom: 25px;
}}

.header h1 {{
    margin: 0 0 8px 0;
    font-size: 30px;
}}

.header p {{
    margin: 4px 0;
    color: #d1d5db;
}}

.cards {{
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(200px, 1fr));

    gap: 18px;
    margin-bottom: 25px;
}}

.card {{
    background: white;
    border-radius: 12px;
    padding: 22px;
    box-shadow:
        0 2px 8px rgba(0,0,0,0.06);
}}

.card-title {{
    font-size: 13px;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

.card-value {{
    margin-top: 8px;
    font-size: 28px;
    font-weight: 700;
}}

.section {{
    background: white;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 25px;

    box-shadow:
        0 2px 8px rgba(0,0,0,0.06);
}}

.section h2 {{
    margin-top: 0;
    margin-bottom: 18px;
}}

.table-container {{
    overflow-x: auto;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    min-width: 850px;
}}

th {{
    background: #f3f4f6;
    text-align: left;
    font-size: 13px;
    padding: 12px;
    white-space: nowrap;
}}

td {{
    padding: 12px;
    border-top: 1px solid #e5e7eb;
    white-space: nowrap;
}}

tr:hover {{
    background: #f9fafb;
}}

.positive {{
    color: #15803d;
}}

.footer {{
    text-align: center;
    color: #6b7280;
    padding: 20px;
    font-size: 13px;
}}

.status {{
    display: inline-block;
    padding: 5px 10px;
    border-radius: 20px;
    background: #dcfce7;
    color: #166534;
    font-size: 13px;
    font-weight: 600;
}}

@media (max-width: 700px) {{

    .container {{
        padding: 15px;
    }}

    .header h1 {{
        font-size: 24px;
    }}

}}

</style>

</head>

<body>

<div class="container">

    <div class="header">

        <h1>
            Trade PnL Attribution Report
        </h1>

        <p>
            End-of-day Trade, Position and PnL Analysis
        </p>

        <p>
            Generated: {generated_at}
        </p>

        <p>
            Currency: {currency}
        </p>

        <p>
            <span class="status">
                Pipeline Completed
            </span>
        </p>

    </div>


    <!-- SUMMARY -->

    <div class="cards">

        <div class="card">

            <div class="card-title">
                Total PnL
            </div>

            <div class="card-value positive">
                {_money(total_pnl)}
            </div>

        </div>


        <div class="card">

            <div class="card-title">
                Realized PnL
            </div>

            <div class="card-value">
                {_money(realized_pnl)}
            </div>

        </div>


        <div class="card">

            <div class="card-title">
                Unrealized PnL
            </div>

            <div class="card-value">
                {_money(unrealized_pnl)}
            </div>

        </div>


        <div class="card">

            <div class="card-title">
                Trading PnL
            </div>

            <div class="card-value">
                {_money(trading_pnl)}
            </div>

        </div>


        <div class="card">

            <div class="card-title">
                Price PnL
            </div>

            <div class="card-value">
                {_money(price_pnl)}
            </div>

        </div>


        <div class="card">

            <div class="card-title">
                Instruments
            </div>

            <div class="card-value">
                {len(instrument_rows)}
            </div>

        </div>

    </div>


    <!-- DAILY BOOK PNL -->

    <div class="section">

        <h2>Daily Book PnL</h2>

        <div class="table-container">

            <table>

                <thead>

                    <tr>
                        <th>Date</th>
                        <th>Book</th>
                        <th>Trading PnL</th>
                        <th>Price PnL</th>
                        <th>Realized PnL</th>
                        <th>Unrealized PnL</th>
                        <th>Total PnL</th>
                        <th>Currency</th>
                    </tr>

                </thead>

                <tbody>

                    {daily_html}

                </tbody>

            </table>

        </div>

    </div>


    <!-- INSTRUMENT PNL -->

    <div class="section">

        <h2>Instrument PnL</h2>

        <div class="table-container">

            <table>

                <thead>

                    <tr>
                        <th>Instrument</th>
                        <th>Book</th>
                        <th>Trading PnL</th>
                        <th>Price PnL</th>
                        <th>Realized PnL</th>
                        <th>Unrealized PnL</th>
                        <th>Total PnL</th>
                        <th>Currency</th>
                    </tr>

                </thead>

                <tbody>

                    {instrument_html}

                </tbody>

            </table>

        </div>

    </div>


    <!-- PNL ATTRIBUTION -->

    <div class="section">

        <h2>PnL Attribution</h2>

        <div class="table-container">

            <table>

                <thead>

                    <tr>
                        <th>Date</th>
                        <th>Book</th>
                        <th>Instrument</th>
                        <th>Trading PnL</th>
                        <th>Price PnL</th>
                        <th>Realized PnL</th>
                        <th>Unrealized PnL</th>
                        <th>Total PnL</th>
                        <th>Currency</th>
                    </tr>

                </thead>

                <tbody>

                    {attribution_html}

                </tbody>

            </table>

        </div>

    </div>


    <!-- POSITIONS -->

    <div class="section">

        <h2>Position Snapshot</h2>

        <div class="table-container">

            <table>

                <thead>

                    <tr>
                        <th>Date</th>
                        <th>Book</th>
                        <th>Instrument</th>
                        <th>Quantity</th>
                        <th>Average Price</th>
                        <th>Market Price</th>
                        <th>Market Value</th>
                        <th>Currency</th>
                    </tr>

                </thead>

                <tbody>

                    {position_html}

                </tbody>

            </table>

        </div>

    </div>


    <!-- FINANCIAL LOGIC -->

    <div class="section">

        <h2>PnL Calculation Methodology</h2>

        <p>
            <strong>Realized PnL</strong>
            = Sold Quantity × (Sell Price − Average Cost)
        </p>

        <p>
            <strong>Unrealized PnL</strong>
            = Closing Quantity × (Market Price − Average Cost)
        </p>

        <p>
            <strong>Total PnL</strong>
            = Realized PnL + Unrealized PnL
        </p>

        <p>
            <strong>PnL Attribution</strong>
            separates trading-related PnL from price-related PnL.
        </p>

    </div>


    <div class="footer">

        Trade PnL Attribution Pipeline
        <br>
        Generated from PostgreSQL reporting views

    </div>

</div>

</body>

</html>
"""

    REPORT_FILE.write_text(
        html,
        encoding="utf-8"
    )

    print(
        f"HTML report generated: {REPORT_FILE}"
    )

    return REPORT_FILE