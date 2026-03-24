from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import UserProfile

from .services import RecommendationEngine, generate_recommendations


class RecommendationEngineTests(TestCase):
	def setUp(self):
		user = get_user_model().objects.create_user(
			username="alice",
			email="alice@example.com",
			password="test-pass-123",
		)
		self.profile = user.profile
		self.profile.is_pregnant = False
		self.profile.dietary_preferences = ""
		self.profile.save(update_fields=["is_pregnant", "dietary_preferences"])

	def test_generate_recommendations_returns_required_fields(self):
		payload = generate_recommendations(
			self.profile,
			sunlight_exposure="low",
			fatigue=True,
		)

		self.assertGreaterEqual(len(payload), 1)
		required = {
			"vitamin_name",
			"reason",
			"food_sources",
			"suggested_frequency",
			"caution_note",
			"priority_label",
		}
		self.assertTrue(required.issubset(payload[0].keys()))

	def test_pregnancy_rule_adds_high_priority_folate(self):
		payload = generate_recommendations(
			self.profile,
			pregnancy_status=True,
		)

		folate = next((item for item in payload if item["vitamin_name"] == "Folate (Vitamin B9)"), None)
		self.assertIsNotNone(folate)
		self.assertEqual(folate["priority_label"], "high")

	def test_low_sunlight_or_history_adds_vitamin_d(self):
		payload = generate_recommendations(
			self.profile,
			sunlight_exposure="low",
			vitamin_d_deficiency_history=True,
		)

		vitamin_d = next((item for item in payload if item["vitamin_name"] == "Vitamin D"), None)
		self.assertIsNotNone(vitamin_d)
		self.assertIn("deficiency", vitamin_d["reason"].lower())

	def test_fatigue_and_iron_history_adds_iron_high_priority(self):
		payload = generate_recommendations(
			self.profile,
			fatigue=True,
			iron_deficiency_history=True,
		)

		iron = next((item for item in payload if item["vitamin_name"] == "Iron"), None)
		self.assertIsNotNone(iron)
		self.assertEqual(iron["priority_label"], "high")

	def test_vegan_restriction_filters_animal_food_sources(self):
		payload = generate_recommendations(
			self.profile,
			diet="vegan",
			fatigue=True,
			sunlight_exposure="low",
		)

		vitamin_d = next((item for item in payload if item["vitamin_name"] == "Vitamin D"), None)
		self.assertIsNotNone(vitamin_d)
		forbidden = {"salmon", "sardines", "fish"}
		self.assertTrue(forbidden.isdisjoint(set(vitamin_d["food_sources"])))

	def test_engine_rejects_invalid_sunlight_exposure(self):
		engine = RecommendationEngine()

		with self.assertRaises(ValueError):
			engine.generate(self.profile, sunlight_exposure="none")
