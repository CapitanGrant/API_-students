from datetime import datetime, timedelta
import pytz
from pydantic import BaseModel, Field, field_validator


class SReferralCodeAdd(BaseModel):
    code: str = Field(..., min_length=3, max_length=15, description="Реферальный код должен быть, от 3 до 15 знаков")
    life_time: datetime = Field(..., description="Cрок годности кода должен быть больше чем 1 день.")
    user_id: int = Field(..., description="ID пользователя, который создает код.")

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        if len(value) < 3 or len(value) > 15:
            raise ValueError('Реферальный код должен быть, от 3 до 15 знаков')
        return value

    @field_validator("life_time")
    @classmethod
    def validate_life_date(cls, value: datetime) -> datetime:
        time_diff = value - datetime.now(pytz.utc)
        if time_diff < timedelta(days=1):
            raise ValueError("Cрок годности кода должен быть больше чем 1 день.")
        return value
