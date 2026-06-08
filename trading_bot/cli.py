"""CLI entry point for the trading bot.

Examples
--------
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

    python cli.py --symbol BTCUSDT --side SELL --type LIMIT \
        --quantity 0.001 --price 65000

    python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT \
        --quantity 0.001 --price 65000 --stop-price 64900

Credentials are read from the environment (or a .env file):
    BINANCE_API_KEY, BINANCE_API_SECRET
"""

import argparse
import os
import sys

from bot.client import BinanceClient, BinanceAPIError
from bot.logging_config import setup_logger
from bot.orders import place_order
from bot.validators import ValidationError, validate_order

logger = setup_logger()


def load_credentials():
    # Optional .env support without a hard dependency.
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        sys.exit(
            "ERROR: Set BINANCE_API_KEY and BINANCE_API_SECRET "
            "(environment variables or a .env file)."
        )
    return api_key, api_secret


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place orders on the Binance Futures Testnet (USDT-M)."
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, help="BUY or SELL")
    parser.add_argument(
        "--type", required=True, dest="order_type",
        help="MARKET, LIMIT, or STOP_LIMIT",
    )
    parser.add_argument("--quantity", required=True, help="Order quantity")
    parser.add_argument("--price", help="Limit price (required for LIMIT/STOP_LIMIT)")
    parser.add_argument("--stop-price", dest="stop_price", help="Stop price (STOP_LIMIT)")
    return parser


def print_summary(title: str, data: dict) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    for key, value in data.items():
        print(f"  {key:<12}: {value}")


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    try:
        params = validate_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValidationError as exc:
        logger.error("Validation failed: %s", exc)
        print(f"Invalid input: {exc}")
        return 2

    print_summary("Order Request Summary", params)

    api_key, api_secret = load_credentials()

    try:
        client = BinanceClient(api_key, api_secret)
        summary = place_order(client, params)
    except BinanceAPIError as exc:
        logger.error("Order failed: %s", exc)
        print(f"\nFAILURE: {exc}")
        return 1
    except Exception as exc:  # noqa: BLE001 - last-resort guard, logged below
        logger.exception("Unexpected error")
        print(f"\nFAILURE: unexpected error: {exc}")
        return 1

    print_summary("Order Response", summary)
    print("\nSUCCESS: order placed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
