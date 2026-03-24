import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .models import SavedClinic
from .services import get_nearby_clinics

logger = logging.getLogger(__name__)


def locator_view(request):
    """Display the clinic locator page with map and search."""
    context = {
        "google_maps_api_key": getattr(settings, "GOOGLE_MAPS_API_KEY", ""),
        "saved_clinics_count": SavedClinic.objects.filter(user=request.user).count()
        if request.user.is_authenticated
        else 0,
    }
    return render(request, "locator/locator.html", context)


@require_http_methods(["GET"])
def nearby_api(request):
    """API endpoint for finding nearby clinics via Google Places.

    Query parameters:
        - latitude (required): Search center latitude
        - longitude (required): Search center longitude
        - radius (optional): Search radius in meters (default: 5000)
        - query (optional): Search term (default: "clinic")

    Returns JSON with list of nearby locations or error message.
    """
    try:
        # Get required parameters
        try:
            latitude = float(request.GET.get("latitude"))
            longitude = float(request.GET.get("longitude"))
        except (ValueError, TypeError):
            return JsonResponse(
                {"error": "Invalid latitude or longitude values"},
                status=400,
            )

        # Validate coordinates
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return JsonResponse(
                {"error": "Coordinates out of valid range"},
                status=400,
            )

        # Get optional parameters
        radius = int(request.GET.get("radius", 5000))
        query = request.GET.get("query", "clinic")

        # Validate radius (reasonable bounds: 500m - 50km)
        if not (500 <= radius <= 50000):
            return JsonResponse(
                {"error": "Radius must be between 500 and 50000 meters"},
                status=400,
            )

        # Get nearby clinics via Google Places
        locations = get_nearby_clinics(latitude, longitude, radius, query)

        # If user is authenticated, mark saved clinics
        saved_place_ids = set()
        if request.user.is_authenticated:
            saved_place_ids = set(
                SavedClinic.objects.filter(user=request.user).values_list(
                    "external_place_id", flat=True
                )
            )

        # Build response data
        results = []
        for location in locations:
            location_dict = location.to_dict()
            location_dict["is_saved"] = location.place_id in saved_place_ids
            results.append(location_dict)

        return JsonResponse(
            {
                "success": True,
                "count": len(results),
                "results": results,
            }
        )

    except Exception as e:
        logger.error(f"Error in nearby_api: {e}")
        return JsonResponse(
            {"error": "An error occurred while searching for nearby clinics"},
            status=500,
        )


@require_http_methods(["POST"])
@login_required
def save_clinic(request):
    """Save a clinic to user's saved list.

    POST data (JSON):
        - place_id: Google Place ID
        - name: Clinic name
        - address: Clinic address
        - latitude: Latitude
        - longitude: Longitude
        - phone (optional): Phone number
        - website (optional): Website URL

    Returns JSON success/error response.
    """
    try:
        data = json.loads(request.body)

        required_fields = ["place_id", "name", "address", "latitude", "longitude"]
        if not all(field in data for field in required_fields):
            return JsonResponse(
                {"error": "Missing required fields"},
                status=400,
            )

        # Parse coordinates
        try:
            latitude = float(data["latitude"])
            longitude = float(data["longitude"])
        except (ValueError, TypeError):
            return JsonResponse(
                {"error": "Invalid coordinates"},
                status=400,
            )

        # Get or create saved clinic
        clinic, created = SavedClinic.objects.update_or_create(
            user=request.user,
            external_place_id=data["place_id"],
            defaults={
                "name": data["name"],
                "address_line": data["address"],
                "latitude": latitude,
                "longitude": longitude,
                "phone": data.get("phone", ""),
                "website": data.get("website", ""),
            },
        )

        return JsonResponse(
            {
                "success": True,
                "message": "Clinic saved successfully",
                "clinic_id": clinic.id,
                "created": created,
            }
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON in request body"},
            status=400,
        )
    except Exception as e:
        logger.error(f"Error saving clinic: {e}")
        return JsonResponse(
            {"error": "An error occurred while saving the clinic"},
            status=500,
        )


@require_http_methods(["POST"])
@login_required
def remove_clinic(request):
    """Remove a clinic from user's saved list.

    POST data (JSON):
        - clinic_id: SavedClinic ID to remove

    Returns JSON success/error response.
    """
    try:
        data = json.loads(request.body)

        if "clinic_id" not in data:
            return JsonResponse(
                {"error": "Missing clinic_id"},
                status=400,
            )

        clinic = SavedClinic.objects.get(id=data["clinic_id"], user=request.user)
        clinic_name = clinic.name
        clinic.delete()

        return JsonResponse(
            {
                "success": True,
                "message": f"{clinic_name} removed from saved clinics",
            }
        )

    except SavedClinic.DoesNotExist:
        return JsonResponse(
            {"error": "Clinic not found"},
            status=404,
        )
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON in request body"},
            status=400,
        )
    except Exception as e:
        logger.error(f"Error removing clinic: {e}")
        return JsonResponse(
            {"error": "An error occurred while removing the clinic"},
            status=500,
        )


@login_required
def saved_clinics_view(request):
    """Display user's saved clinics."""
    saved_clinics = SavedClinic.objects.filter(user=request.user)
    context = {
        "saved_clinics": saved_clinics,
        "google_maps_api_key": getattr(settings, "GOOGLE_MAPS_API_KEY", ""),
    }
    return render(request, "locator/saved_clinics.html", context)

