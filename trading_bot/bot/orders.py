"""Order placement logic.

Translates validated, normalized order parameters into Binance API payloads
and returns a tidy summary of the result.
"""

from .client import BinanceClient
from .logging_config import setup_logger

logger = setup_logger()


def build_payload(params: dict) -> dict:
    """Convert validated params into a Binance Futures order payload."""
    order_type = params["order_type"]

    payload = {
        "symbol": params["symbol"],
        "side": params["side"],
        "quantity": params["quantity"],
    }

    if order_type == "MARKET":
        payload["type"] = "MARKET"
    elif order_type == "LIMIT":
        payload["type"] = "LIMIT"
        payload["price"] = params["price"]
        payload["timeInForce"] = "GTC"
    elif order_type == "STOP_LIMIT":
        # Binance Futures stop-limit uses type=STOP with price + stopPrice.
        payload["type"] = "STOP"
        payload["price"] = params["price"]
        payload["stopPrice"] = params["stop_price"]
        payload["timeInForce"] = "GTC"
    else:
        raise ValueError(f"Unsupported order type: {order_type}")

    return payload


def summarize_response(response: dict) -> dict:
    """Pull the fields the task asks us to display."""
    return {
        "orderId": response.get("orderId"),
        "status": response.get("status"),
        "executedQty": response.get("executedQty"),
        "avgPrice": response.get("avgPrice"),
        "symbol": response.get("symbol"),
        "side": response.get("side"),
        "type": response.get("type"),
    }


def place_order(client: BinanceClient, params: dict) -> dict:
    """Build, send, and summarize an order. Raises on API/network failure."""
    payload = build_payload(params)
    logger.info("Placing order: %s", payload)
    response = client.place_order(payload)
    summary = summarize_response(response)
    logger.info("Order summary: %s", summary)
    return summary
