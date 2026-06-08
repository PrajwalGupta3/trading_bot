"""Input validation for order parameters.

These validators run before any network call so that obviously bad input is
rejected with a clear message instead of bouncing off the Binance API.
"""

from decimal import Decimal, InvalidOperation

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_LIMIT"}


class ValidationError(ValueError):
    """Raised when user-supplied order parameters are invalid."""


def validate_symbol(symbol: str) -> str:
    if not symbol or not symbol.isalnum():
        raise ValidationError(f"Invalid symbol: {symbol!r}. Expected something like BTCUSDT.")
    return symbol.upper()


def validate_side(side: str) -> str:
    side = side.upper()
    if side not in VALID_SIDES:
        raise ValidationError(f"Invalid side: {side!r}. Must be one of {sorted(VALID_SIDES)}.")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type: {order_type!r}. Must be one of {sorted(VALID_ORDER_TYPES)}."
        )
    return order_type


def validate_positive_number(value, field_name: str) -> float:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ValidationError(f"{field_name} must be a number, got {value!r}.")
    if number <= 0:
        raise ValidationError(f"{field_name} must be greater than 0, got {value}.")
    return float(number)


def validate_order(symbol, side, order_type, quantity, price=None, stop_price=None) -> dict:
    """Validate a complete order request and return a normalized dict."""
    order_type = validate_order_type(order_type)

    params = {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": order_type,
        "quantity": validate_positive_number(quantity, "quantity"),
    }

    if order_type in ("LIMIT", "STOP_LIMIT"):
        if price is None:
            raise ValidationError(f"price is required for {order_type} orders.")
        params["price"] = validate_positive_number(price, "price")

    if order_type == "STOP_LIMIT":
        if stop_price is None:
            raise ValidationError("stop_price is required for STOP_LIMIT orders.")
        params["stop_price"] = validate_positive_number(stop_price, "stop_price")

    return params
