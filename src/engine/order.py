from enum import Enum
from typing import Optional, Dict, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    IOC = "ioc"
    FOK = "fok"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(str, Enum):
    NEW = "new"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"

class Order(BaseModel):
    order_id: str = Field(..., description="Unique order identifier")
    symbol: str = Field(..., description="Trading pair symbol")
    order_type: OrderType
    side: OrderSide
    quantity: float
    price: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: OrderStatus = OrderStatus.NEW
    filled_quantity: float = 0.0
    remaining_quantity: float = Field(..., description="Quantity remaining to be filled")
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.remaining_quantity is None:
            self.remaining_quantity = self.quantity
        self._update_status()

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v

    def _update_status(self) -> None:
        """Update order status based on filled quantity"""
        if self.filled_quantity == 0:
            self.status = OrderStatus.NEW
        elif self.filled_quantity < self.quantity:
            self.status = OrderStatus.PARTIAL
        else:
            self.status = OrderStatus.FILLED

    @property
    def is_marketable(self) -> bool:
        """Check if order can be executed immediately"""
        return (
            self.order_type == OrderType.MARKET
            or self.order_type in [OrderType.IOC, OrderType.FOK]
            or (self.order_type == OrderType.LIMIT and self.price is not None)
        )