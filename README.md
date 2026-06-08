# Simplified Trading Bot — Binance Futures Testnet (USDT-M)

A small Python CLI that places **Market**, **Limit**, and (bonus) **Stop-Limit**
orders on the Binance Futures Testnet, with a clean client/CLI separation,
structured logging, and input validation.

## Features

- Place **MARKET** and **LIMIT** orders (BUY/SELL)
- Bonus third order type: **STOP_LIMIT**
- CLI input via `argparse` with validation before any network call
- Clear output: order request summary, response details (orderId, status,
  executedQty, avgPrice), and a success/failure message
- Structured code: API layer (`bot/client.py`) separate from order logic
  (`bot/orders.py`), validation (`bot/validators.py`), and CLI (`cli.py`)
- All API requests, responses, and errors logged to `logs/trading_bot.log`
  (rotating file handler; signatures redacted)

## Project structure

```
trading_bot/
  bot/
    __init__.py
    client.py          # Binance signed REST client wrapper
    orders.py          # order payload building + placement
    validators.py      # input validation
    logging_config.py  # rotating file + console logging
  cli.py               # CLI entry point
  requirements.txt
  .env.example
  README.md
  logs/                # log files written here
```

## Setup

1. Register and activate a **Binance Futures Testnet** account at
   <https://testnet.binancefuture.com> and generate API credentials.

2. Clone the repo and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Provide credentials. Copy `.env.example` to `.env` and fill it in:

   ```bash
   cp .env.example .env
   ```

   ```
   BINANCE_API_KEY=your_testnet_api_key_here
   BINANCE_API_SECRET=your_testnet_api_secret_here
   ```

   (Or export `BINANCE_API_KEY` / `BINANCE_API_SECRET` as environment variables.)

## Usage

Market order:

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

Limit order (price required):

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 65000
```

Stop-limit order (bonus; price + stop-price required):

```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT \
    --quantity 0.001 --price 65000 --stop-price 64900
```

### Example output

```
Order Request Summary
---------------------
  symbol      : BTCUSDT
  side        : BUY
  order_type  : MARKET
  quantity    : 0.001

Order Response
--------------
  orderId     : 123456789
  status      : FILLED
  executedQty : 0.001
  avgPrice    : 64850.20
  ...

SUCCESS: order placed.
```

## Logging

Logs are written to `logs/trading_bot.log`. The file handler captures DEBUG+
detail (requests, responses, errors with the API signature redacted); the
console only surfaces warnings and errors so normal runs stay quiet.

## Assumptions

- Quantity/price precision must match Binance's symbol filters; the bot sends
  values as given and surfaces any Binance filter error rather than rounding.
- `recvWindow` is fixed at 5000 ms.
- Direct signed REST calls (`requests`) are used instead of `python-binance`
  to keep dependencies minimal; the base URL is the testnet host.
- Stop-limit is implemented via Binance Futures `type=STOP` (price + stopPrice).
```
