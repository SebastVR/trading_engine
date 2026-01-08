from enum import Enum


class SignalType(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class TradeSide(str, Enum):
    long = "long"
    short = "short"


class TradeStatus(str, Enum):
    open = "open"
    closed = "closed"


class TradeResult(str, Enum):
    win = "win"
    loss = "loss"
    unknown = "unknown"
