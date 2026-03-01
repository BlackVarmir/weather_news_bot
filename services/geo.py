"""
services/geo.py — Визначення країни за назвою міста або координатами.
Використовує geopy (Nominatim — безкоштовний geocoder OpenStreetMap).
"""
import logging
import asyncio
from typing import Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GeoLocation:
    city: str
    country: str
    country_code: str  # ISO 3166-1 alpha-2
    latitude: float
    longitude: float


class GeoService:
    """Сервіс геолокації на базі geopy Nominatim."""

    def __init__(self):
        # Nominatim вимагає user_agent
        from geopy.geocoders import Nominatim
        self._geocoder = Nominatim(user_agent="weather_news_bot_v1")

    async def get_location_by_city(
        self, city: str
    ) -> Optional[List[GeoLocation]]:
        """
        Знаходить локації за назвою міста.
        Повертає список (може бути кілька міст з однаковою назвою).
        """
        try:
            locations = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._geocoder.geocode(
                    city,
                    exactly_one=False,
                    limit=5,
                    language="en",
                    addressdetails=True,
                ),
            )
            if not locations:
                return None

            results = []
            seen = set()  # дедублікація

            for loc in locations:
                address = loc.raw.get("address", {})
                country = address.get("country", "")
                country_code = address.get("country_code", "").upper()
                city_name = (
                    address.get("city")
                    or address.get("town")
                    or address.get("village")
                    or city
                )

                key = f"{city_name}:{country_code}"
                if key in seen:
                    continue
                seen.add(key)

                results.append(
                    GeoLocation(
                        city=city_name,
                        country=country,
                        country_code=country_code,
                        latitude=loc.latitude,
                        longitude=loc.longitude,
                    )
                )

            return results if results else None

        except Exception as e:
            logger.error(f"Помилка геокодування міста '{city}': {e}")
            return None

    async def get_location_by_coords(
        self, lat: float, lon: float
    ) -> Optional[GeoLocation]:
        """
        Визначає місто та країну за GPS-координатами (reverse geocoding).
        """
        try:
            location = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._geocoder.reverse(
                    (lat, lon), language="en", addressdetails=True
                ),
            )
            if not location:
                return None

            address = location.raw.get("address", {})
            city_name = (
                address.get("city")
                or address.get("town")
                or address.get("village")
                or address.get("county")
                or "Unknown"
            )
            country = address.get("country", "")
            country_code = address.get("country_code", "").upper()

            return GeoLocation(
                city=city_name,
                country=country,
                country_code=country_code,
                latitude=lat,
                longitude=lon,
            )

        except Exception as e:
            logger.error(f"Помилка reverse geocoding ({lat}, {lon}): {e}")
            return None
