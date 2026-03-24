from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.utils import timezone

from .models import VitaminLog

if TYPE_CHECKING:
    from django.contrib.auth.models import User

user_model = get_user_model()


@dataclass(frozen=True)
class TrackingSummary:
    days_logged_7: int
    days_logged_30: int
    adherence_7: int
    adherence_30: int
    total_logs_30: int
    current_streak_days: int


def _current_streak_days(logs: QuerySet[VitaminLog]) -> int:
    dates = list(logs.values_list("logged_for", flat=True).distinct().order_by("-logged_for"))
    if not dates:
        return 0

    today = timezone.localdate()
    expected_date = today

    # If there is no log today but there is one yesterday, streak can continue from yesterday.
    if dates[0] == today - timedelta(days=1):
        expected_date = today - timedelta(days=1)

    streak = 0
    date_set = set(dates)
    while expected_date in date_set:
        streak += 1
        expected_date -= timedelta(days=1)
    return streak


def build_tracking_summary(user: User) -> TrackingSummary:
    today = timezone.localdate()
    last_30_start = today - timedelta(days=29)
    last_7_start = today - timedelta(days=6)

    logs_last_30 = VitaminLog.objects.filter(user=user, logged_for__gte=last_30_start)
    logs_last_7 = logs_last_30.filter(logged_for__gte=last_7_start)

    days_logged_30 = logs_last_30.values("logged_for").distinct().count()
    days_logged_7 = logs_last_7.values("logged_for").distinct().count()

    adherence_30 = round((days_logged_30 / 30) * 100) if days_logged_30 else 0
    adherence_7 = round((days_logged_7 / 7) * 100) if days_logged_7 else 0

    return TrackingSummary(
        days_logged_7=days_logged_7,
        days_logged_30=days_logged_30,
        adherence_7=adherence_7,
        adherence_30=adherence_30,
        total_logs_30=logs_last_30.count(),
        current_streak_days=_current_streak_days(VitaminLog.objects.filter(user=user)),
    )
