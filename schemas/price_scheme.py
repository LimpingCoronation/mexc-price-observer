from datetime import datetime
from pydantic import BaseModel


class PriceScheme(BaseModel):
    created_at: datetime
    price: float
    volume: float
    volume_cur: float
