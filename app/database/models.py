from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class Airport:
    name: Optional[str] = None
    city_code: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    city_id: Optional[int] = None
    country_id: Optional[int] = None


@dataclass
class City:
    name: Optional[str] = None
    code: Optional[str] = None
    country_code: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None


@dataclass
class Subscription:
    departure_city_code: Optional[str] = None
    arrival_city_code: Optional[str] = None
