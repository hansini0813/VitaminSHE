"""
Google Places API integration service for finding nearby clinics and medical facilities.

This module provides an abstraction layer for searching nearby locations using
the Google Places API. It can be easily swapped for alternative providers
(e.g., OpenStreetMap, Bing Maps) without changing the views.
"""

import logging
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlencode

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class NearbyLocation:
    """Represents a nearby location found via Google Places API."""

    place_id: str
    name: str
    address: str
    latitude: float
    longitude: float
    distance_meters: Optional[float] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    open_now: Optional[bool] = None
    types: list = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "place_id": self.place_id,
            "name": self.name,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "distance_meters": self.distance_meters,
            "phone": self.phone,
            "website": self.website,
            "rating": self.rating,
            "open_now": self.open_now,
            "types": self.types or [],
        }


class GooglePlacesService:
    """Service for interacting with Google Places API.

    This service handles all communication with Google Places API and normalizes
    responses into NearbyLocation objects. API key should be set in Django settings
    as GOOGLE_PLACES_API_KEY.
    """

    # Query terms for finding medical facilities
    MEDICAL_KEYWORDS = [
        "clinic",
        "blood test",
        "phlebotomy",
        "diagnostic center",
        "laboratory",
        "medical center",
        "urgent care",
    ]

    # Place types that indicate medical facilities
    MEDICAL_PLACE_TYPES = [
        "health",
        "doctor",
        "hospital",
        "pharmacy",
        "medical_care",
        "physiotherapist",
        "dentist",
    ]

    def __init__(self):
        """Initialize service with Google Places API key."""
        self.api_key = getattr(settings, "GOOGLE_PLACES_API_KEY", None)
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        if not self.api_key:
            logger.warning("GOOGLE_PLACES_API_KEY not configured in settings")

    def search_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int = 5000,
        query: str = "clinic",
    ) -> list[NearbyLocation]:
        """Search for nearby locations using Google Places Nearby Search.

        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius_meters: Search radius in meters (default 5000)
            query: Search query term (default "clinic")

        Returns:
            List of NearbyLocation objects or empty list if API call fails
        """
        if not self.api_key:
            logger.error("Google Places API key not configured")
            return []

        try:
            # Use Nearby Search endpoint
            endpoint = f"{self.base_url}/nearbysearch/json"
            params = {
                "location": f"{latitude},{longitude}",
                "radius": radius_meters,
                "keyword": query,
                "type": "health",  # Restricts results to health-related places
                "key": self.api_key,
            }

            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get("status") != "OK":
                logger.warning(f"Google Places API returned status: {data.get('status')}")
                return []

            locations = []
            for result in data.get("results", []):
                location = self._parse_place_result(result, latitude, longitude)
                if location:
                    locations.append(location)

            return locations

        except requests.RequestException as e:
            logger.error(f"Google Places API request failed: {e}")
            return []
        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing Google Places response: {e}")
            return []

    def get_place_details(self, place_id: str) -> Optional[dict]:
        """Fetch detailed information about a specific place.

        Args:
            place_id: Google Place ID

        Returns:
            Dictionary with detailed place information or None if request fails
        """
        if not self.api_key:
            logger.error("Google Places API key not configured")
            return None

        try:
            endpoint = f"{self.base_url}/details/json"
            params = {
                "place_id": place_id,
                "fields": "name,formatted_address,formatted_phone_number,website,opening_hours,rating,reviews",
                "key": self.api_key,
            }

            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get("status") == "OK":
                return data.get("result")

            logger.warning(f"Google Places details call returned status: {data.get('status')}")
            return None

        except requests.RequestException as e:
            logger.error(f"Google Places details request failed: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing Google Places details: {e}")
            return None

    def _parse_place_result(
        self,
        result: dict,
        center_latitude: float,
        center_longitude: float,
    ) -> Optional[NearbyLocation]:
        """Parse a single result from Google Places API response.

        Args:
            result: Single result object from Google Places API
            center_latitude: Reference latitude for distance calculation
            center_longitude: Reference longitude for distance calculation

        Returns:
            NearbyLocation object or None if parsing fails
        """
        try:
            lat = result["geometry"]["location"]["lat"]
            lng = result["geometry"]["location"]["lng"]

            # Calculate approximate distance using Haversine formula
            distance = self._haversine_distance(
                center_latitude, center_longitude, lat, lng
            )

            location = NearbyLocation(
                place_id=result.get("place_id", ""),
                name=result.get("name", "Unknown"),
                address=result.get("vicinity", ""),
                latitude=lat,
                longitude=lng,
                distance_meters=distance,
                rating=result.get("rating"),
                types=result.get("types", []),
            )

            # Fetch detailed information if available
            if location.place_id:
                details = self.get_place_details(location.place_id)
                if details:
                    location.phone = details.get("formatted_phone_number")
                    location.website = details.get("website")
                    location.address = details.get("formatted_address", location.address)

            return location

        except (KeyError, TypeError, ValueError) as e:
            logger.warning(f"Could not parse place result: {e}")
            return None

    @staticmethod
    def _haversine_distance(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """Calculate distance between two coordinates using Haversine formula.

        Args:
            lat1, lon1: First coordinate in decimal degrees
            lat2, lon2: Second coordinate in decimal degrees

        Returns:
            Distance in meters
        """
        import math

        R = 6371000  # Earth's radius in meters

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        return R * c


def get_nearby_clinics(
    latitude: float,
    longitude: float,
    radius_meters: int = 5000,
    query: str = "clinic",
) -> list[NearbyLocation]:
    """Convenience function to find nearby clinics.

    Args:
        latitude: Center point latitude
        longitude: Center point longitude
        radius_meters: Search radius in meters (default 5000)
        query: Search query (default "clinic")

    Returns:
        List of NearbyLocation objects
    """
    service = GooglePlacesService()
    return service.search_nearby(latitude, longitude, radius_meters, query)
