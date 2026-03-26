from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from accounts.models import UserProfile
from .services import (
    calculate_age_from_date,
    compute_age_range,
    get_vitamin_recommendations,
    get_vitamin_details,
    get_all_vitamins_info,
    generate_recommendations,
)


@login_required
def dashboard(request):
    """Display personalized vitamin recommendations for the logged-in user."""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(user=request.user)
    
    # Calculate age if date of birth is available
    age = None
    if profile.date_of_birth:
        age = calculate_age_from_date(profile.date_of_birth)
    
    # Get vitamin recommendations
    recommendations = {}
    if age is not None:
        recommendations = get_vitamin_recommendations(
            age,
            is_pregnant=profile.is_pregnant,
            is_breastfeeding=profile.is_breastfeeding,
        )
    
    # Get personalized recommendations
    personalized = generate_recommendations(
        profile,
        pregnancy_status=profile.is_pregnant,
    )
    
    context = {
        "profile": profile,
        "age": age,
        "age_range": compute_age_range(age, profile.is_pregnant, profile.is_breastfeeding) if age else None,
        "vitamin_recommendations": recommendations,
        "personalized_recommendations": personalized,
    }
    
    return render(request, "recommendations/dashboard.html", context)


@login_required
def resources(request):
    """Display educational resources about vitamins and minerals."""
    vitamins_info = get_all_vitamins_info()
    
    # Organize by category
    categories = {}
    for vitamin_id, info in vitamins_info.items():
        category = info.get("category", "Other")
        if category not in categories:
            categories[category] = []
        categories[category].append({
            "id": vitamin_id,
            "name": info.get("name", ""),
            "description": info.get("description", ""),
            "benefits": info.get("benefits", []),
        })
    
    context = {
        "categories": {cat: sorted(vits, key=lambda x: x["name"]) for cat, vits in sorted(categories.items())},
        "total_vitamins": len(vitamins_info),
    }
    
    return render(request, "recommendations/resources.html", context)


@login_required
def vitamin_detail(request, vitamin_id):
    """Display detailed information about a specific vitamin."""
    vitamin_info = get_vitamin_details(vitamin_id)
    
    if not vitamin_info:
        return render(request, "recommendations/vitamin_not_found.html", status=404)
    
    # Get user's requirement for this vitamin if available
    try:
        profile = request.user.profile
        age = None
        if profile.date_of_birth:
            age = calculate_age_from_date(profile.date_of_birth)
        
        user_requirement = None
        if age is not None:
            recommendations = get_vitamin_recommendations(
                age,
                is_pregnant=profile.is_pregnant,
                is_breastfeeding=profile.is_breastfeeding,
            )
            user_requirement = recommendations.get(vitamin_id)
    except UserProfile.DoesNotExist:
        user_requirement = None
    
    context = {
        "vitamin_id": vitamin_id,
        "vitamin": vitamin_info,
        "user_requirement": user_requirement,
    }
    
    return render(request, "recommendations/vitamin_detail.html", context)


@require_http_methods(["GET"])
def api_vitamin_recommendations(request):
    """API endpoint to get vitamin recommendations for the logged-in user."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        return JsonResponse({"error": "User profile not found"}, status=404)
    
    age = None
    if profile.date_of_birth:
        age = calculate_age_from_date(profile.date_of_birth)
    
    if age is None:
        return JsonResponse({"error": "Date of birth not set"}, status=400)
    
    recommendations = get_vitamin_recommendations(
        age,
        is_pregnant=profile.is_pregnant,
        is_breastfeeding=profile.is_breastfeeding,
    )
    
    return JsonResponse({
        "age": age,
        "age_range": compute_age_range(age, profile.is_pregnant, profile.is_breastfeeding),
        "is_pregnant": profile.is_pregnant,
        "is_breastfeeding": profile.is_breastfeeding,
        "recommendations": recommendations,
    })


@require_http_methods(["GET"])
def api_all_vitamins(request):
    """API endpoint to get information about all vitamins."""
    vitamins_info = get_all_vitamins_info()
    return JsonResponse(vitamins_info)


@require_http_methods(["GET"])
def api_vitamin_detail(request, vitamin_id):
    """API endpoint to get detailed information about a specific vitamin."""
    vitamin_info = get_vitamin_details(vitamin_id)
    
    if not vitamin_info:
        return JsonResponse({"error": "Vitamin not found"}, status=404)
    
    return JsonResponse(vitamin_info)


def index(request):
    """Placeholder view for recommendations module."""
    return render(request, "recommendations/index.html")
