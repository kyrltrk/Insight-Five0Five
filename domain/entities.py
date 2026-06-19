from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Indicator:
    code: str
    name: str


@dataclass(frozen=True)
class IndicatorValue:
    country: str
    indicator_code: str
    year: int
    value: Optional[float]
