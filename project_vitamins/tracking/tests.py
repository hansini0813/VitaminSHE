from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import VitaminLog
from .services import build_tracking_summary


class VitaminTrackingViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user("owner", "owner@example.com", "pw12345678")
        self.other = user_model.objects.create_user("other", "other@example.com", "pw12345678")

        self.owner_log = VitaminLog.objects.create(
            user=self.owner,
            vitamin_type=VitaminLog.VitaminType.VITAMIN_D,
            intake_source=VitaminLog.IntakeSource.SUPPLEMENT,
            amount=1000,
            unit=VitaminLog.Unit.IU,
            logged_for=timezone.localdate(),
        )

    def test_list_view_shows_only_owner_records(self):
        VitaminLog.objects.create(
            user=self.other,
            vitamin_type=VitaminLog.VitaminType.IRON,
            intake_source=VitaminLog.IntakeSource.FOOD,
            amount=10,
            unit=VitaminLog.Unit.MG,
            logged_for=timezone.localdate(),
        )

        self.client.login(username="owner", password="pw12345678")
        response = self.client.get(reverse("tracking:index"))

        self.assertEqual(response.status_code, 200)
        logs = list(response.context["logs"])
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].user, self.owner)

    def test_edit_other_user_record_returns_404(self):
        other_log = VitaminLog.objects.create(
            user=self.other,
            vitamin_type=VitaminLog.VitaminType.VITAMIN_C,
            intake_source=VitaminLog.IntakeSource.FOOD,
            amount=75,
            unit=VitaminLog.Unit.MG,
            logged_for=timezone.localdate(),
        )

        self.client.login(username="owner", password="pw12345678")
        response = self.client.get(reverse("tracking:edit", kwargs={"pk": other_log.pk}))

        self.assertEqual(response.status_code, 404)

    def test_delete_other_user_record_returns_404(self):
        other_log = VitaminLog.objects.create(
            user=self.other,
            vitamin_type=VitaminLog.VitaminType.VITAMIN_C,
            intake_source=VitaminLog.IntakeSource.FOOD,
            amount=75,
            unit=VitaminLog.Unit.MG,
            logged_for=timezone.localdate(),
        )

        self.client.login(username="owner", password="pw12345678")
        response = self.client.post(reverse("tracking:delete", kwargs={"pk": other_log.pk}))

        self.assertEqual(response.status_code, 404)


class TrackingSummaryTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("summary", "summary@example.com", "pw12345678")

    def test_summary_calculates_adherence_and_streak(self):
        today = timezone.localdate()

        # Build a 3-day streak (today, yesterday, two days ago) and one older entry.
        for day_offset in [0, 1, 2, 10]:
            VitaminLog.objects.create(
                user=self.user,
                vitamin_type=VitaminLog.VitaminType.VITAMIN_D,
                intake_source=VitaminLog.IntakeSource.SUPPLEMENT,
                amount=1000,
                unit=VitaminLog.Unit.IU,
                logged_for=today - timedelta(days=day_offset),
            )

        summary = build_tracking_summary(self.user)

        self.assertEqual(summary.current_streak_days, 3)
        self.assertGreaterEqual(summary.days_logged_7, 3)
        self.assertGreaterEqual(summary.days_logged_30, 4)
        self.assertGreater(summary.adherence_7, 0)
        self.assertGreater(summary.adherence_30, 0)
