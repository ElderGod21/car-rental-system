from datetime import datetime
from pydantic import BaseModel

class Car(BaseModel):
    make: str
    model: str
    year: int
    daily_rate: float
    available: bool = True

class CarRental(BaseModel):
    user_name: str
    start_date: datetime
    end_date: datetime
    rental_date: datetime = datetime.now()