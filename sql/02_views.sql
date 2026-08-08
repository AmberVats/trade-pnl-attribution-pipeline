-- ============================================================
-- Trade PnL Attribution Pipeline
-- Reporting Views
-- ============================================================

-- Daily PnL attribution by book and instrument

CREATE OR REPLACE VIEW vw_daily_pnl_attribution AS
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
    instrument_id;


-- Daily PnL summary by book

CREATE OR REPLACE VIEW vw_daily_book_pnl AS
SELECT
    attribution_date,
    book,
    SUM(trading_pnl) AS trading_pnl,
    SUM(price_pnl) AS price_pnl,
    SUM(realized_pnl) AS realized_pnl,
    SUM(unrealized_pnl) AS unrealized_pnl,
    SUM(total_pnl) AS total_pnl,
    currency
FROM fct_pnl_attribution
GROUP BY
    attribution_date,
    book,
    currency
ORDER BY
    attribution_date,
    book;


-- Instrument-level PnL summary

CREATE OR REPLACE VIEW vw_instrument_pnl AS
SELECT
    instrument_id,
    book,
    SUM(trading_pnl) AS trading_pnl,
    SUM(price_pnl) AS price_pnl,
    SUM(realized_pnl) AS realized_pnl,
    SUM(unrealized_pnl) AS unrealized_pnl,
    SUM(total_pnl) AS total_pnl,
    currency
FROM fct_pnl_attribution
GROUP BY
    instrument_id,
    book,
    currency
ORDER BY
    instrument_id,
    book;