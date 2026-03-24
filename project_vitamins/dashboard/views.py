from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.models import UserProfile
from recommendations.models import Recommendation
from recommendations.services import generate_recommendations
from tracking.models import VitaminLog
from tracking.services import build_tracking_summary


@login_required
def index(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if profile.onboarding_status == UserProfile.OnboardingStatus.PENDING:
        return redirect("accounts:onboarding")

    recent_logs = (
        VitaminLog.objects.filter(user=request.user)
        .order_by("-logged_for", "-created_at")[:6]
    )

    summary = build_tracking_summary(request.user)

    recommendation_cards = list(
        Recommendation.objects.filter(user=request.user, is_active=True)
        .order_by("-updated_at")[:6]
        .values(
            "title",
            "description",
            "recommendation_type",
            "starts_on",
            "ends_on",
        )
    )

    if not recommendation_cards:
        recommendation_cards = generate_recommendations(
            profile,
            diet=profile.dietary_preferences,
            pregnancy_status=profile.is_pregnant,
            sunlight_exposure="moderate",
            fatigue=False,
            iron_deficiency_history=False,
            vitamin_d_deficiency_history=False,
            health_goals=["energy", "bone health"],
            allergies_restrictions=[],
        )

    context = {
        "profile": profile,
        "recent_logs": recent_logs,
        "recommendation_cards": recommendation_cards,
        "stats": {
            "days_logged_30": summary.days_logged_30,
            "days_logged_7": summary.days_logged_7,
            "adherence_30": summary.adherence_30,
            "adherence_7": summary.adherence_7,
            "total_logs": summary.total_logs_30,
            "current_streak_days": summary.current_streak_days,
        },
    }
    return render(request, "dashboard/index.html", context)