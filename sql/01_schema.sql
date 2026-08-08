-- ============================================================
-- Trade PnL Attribution Pipeline
-- Database Schema
-- ============================================================

-- ------------------------------------------------------------
-- 1. Instrument dimension
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dim_instrument (
    instrument_id      VARCHAR(50) PRIMARY KEY,
    symbol             VARCHAR(50) NOT NULL,
    instrument_type    VARCHAR(30) NOT NULL,
    currency           VARCHAR(10) NOT NULL,
    exchange           VARCHAR(50),
    sector             VARCHAR(100),
    active             BOOLEAN NOT NULL DEFAULT TRUE,
    created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ------------------------------------------------------------
-- 2. Trade fact table
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fct_trade (
    trade_id           BIGSERIAL PRIMARY KEY,
    trade_date         DATE NOT NULL,
    book               VARCHAR(50) NOT NULL,
    instrument_id      VARCHAR(50) NOT NULL,
    side               VARCHAR(10) NOT NULL,
    quantity           NUMERIC(20, 6) NOT NULL,
    price              NUMERIC(20, 8) NOT NULL,
    currency           VARCHAR(10) NOT NULL,
    trader             VARCHAR(100),
    created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_trade_instrument
        FOREIGN KEY (instrument_id)
        REFERENCES dim_instrument(instrument_id),

    CONSTRAINT chk_trade_side
        CHECK (side IN ('BUY', 'SELL')),

    CONSTRAINT chk_trade_quantity
        CHECK (quantity > 0),

    CONSTRAINT chk_trade_price
        CHECK (price >= 0)
);


-- ------------------------------------------------------------
-- 3. Market price fact table
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fct_market_price (
    price_date         DATE NOT NULL,
    instrument_id      VARCHAR(50) NOT NULL,
    close_price        NUMERIC(20, 8) NOT NULL,
    currency           VARCHAR(10) NOT NULL,
    source             VARCHAR(50),

    PRIMARY KEY (price_date, instrument_id),

    CONSTRAINT fk_market_price_instrument
        FOREIGN KEY (instrument_id)
        REFERENCES dim_instrument(instrument_id),

    CONSTRAINT chk_market_price
        CHECK (close_price >= 0)
);


-- ------------------------------------------------------------
-- 4. EOD position fact table
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fct_position (
    position_date      DATE NOT NULL,
    book               VARCHAR(50) NOT NULL,
    instrument_id      VARCHAR(50) NOT NULL,
    quantity           NUMERIC(20, 6) NOT NULL,
    average_price      NUMERIC(20, 8),
    market_price       NUMERIC(20, 8),
    market_value       NUMERIC(30, 8),
    currency           VARCHAR(10) NOT NULL,

    PRIMARY KEY (position_date, book, instrument_id),

    CONSTRAINT fk_position_instrument
        FOREIGN KEY (instrument_id)
        REFERENCES dim_instrument(instrument_id)
);


-- ------------------------------------------------------------
-- 5. PnL fact table
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fct_pnl (
    pnl_date           DATE NOT NULL,
    book               VARCHAR(50) NOT NULL,
    instrument_id      VARCHAR(50) NOT NULL,
    realized_pnl       NUMERIC(30, 8) NOT NULL DEFAULT 0,
    unrealized_pnl     NUMERIC(30, 8) NOT NULL DEFAULT 0,
    total_pnl          NUMERIC(30, 8) NOT NULL DEFAULT 0,
    currency           VARCHAR(10) NOT NULL,

    PRIMARY KEY (pnl_date, book, instrument_id),

    CONSTRAINT fk_pnl_instrument
        FOREIGN KEY (instrument_id)
        REFERENCES dim_instrument(instrument_id)
);