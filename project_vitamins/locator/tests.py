import json

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from .models import SavedClinic
from .services import GooglePlacesService, NearbyLocation


class NearbyAPITests(TestCase):
    """Test the clinic nearby search API endpoint."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_nearby_api_requires_coordinates(self):
        """Test that API requires latitude and longitude."""
        response = self.client.get(reverse("locator:nearby_api"))
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("error", data)

    def test_nearby_api_validates_latitude_range(self):
        """Test that API validates latitude is within -90 to 90."""
        response = self.client.get(
            reverse("locator:nearby_api"),
            {
                "latitude": 95,  # Invalid
                "longitude": -74,
            },
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("error", data)

    def test_nearby_api_validates_longitude_range(self):
        """Test that API validates longitude is within -180 to 180."""
        response = self.client.get(
            reverse("locator:nearby_api"),
            {
                "latitude": 40,
                "longitude": 200,  # Invalid
            },
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("error", data)

    def test_nearby_api_validates_radius_range(self):
        """Test that API validates radius is between 500 and 50000 meters."""
        # Too small
        response = self.client.get(
            reverse("locator:nearby_api"),
            {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "radius": 100,
            },
        )
        self.assertEqual(response.status_code, 400)

        # Too large
        response = self.client.get(
            reverse("locator:nearby_api"),
            {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "radius": 100000,
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_nearby_api_accepts_valid_coordinates(self):
        """Test that API accepts valid coordinates."""
        response = self.client.get(
            reverse("locator:nearby_api"),
            {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "radius": 5000,
                "query": "clinic",
            },
        )
        # Will return 200 even if API key not set (returns empty results)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("success", data)
        self.assertIn("results", data)
        self.assertIn("count", data)

    def test_nearby_api_response_format(self):
        """Test that API returns correctly formatted JSON."""
        response = self.client.get(
            reverse("locator:nearby_api"),
            {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "radius": 5000,
            },
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["success"])
        self.assertIsInstance(data["results"], list)
        self.assertIsInstance(data["count"], int)


class SaveClinicAPITests(TestCase):
    """Test the save clinic API endpoint."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_save_clinic_requires_authentication(self):
        """Test that save clinic endpoint requires authentication."""
        response = self.client.post(
            reverse("locator:save_clinic"),
            data=json.dumps(
                {
                    "place_id": "test123",
                    "name": "Test Clinic",
                    "address": "123 Main St",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_save_clinic_requires_fields(self):
        """Test that save clinic endpoint requires all fields."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("locator:save_clinic"),
            data=json.dumps(
                {
                    "place_id": "test123",
                    # Missing required fields
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("error", data)

    def test_save_clinic_success(self):
        """Test successful clinic save."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("locator:save_clinic"),
            data=json.dumps(
                {
                    "place_id": "test123",
                    "name": "Test Clinic",
                    "address": "123 Main St",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "phone": "555-1234",
                    "website": "https://testclinic.com",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["success"])
        self.assertIn("clinic_id", data)

        # Verify clinic was created
        clinic = SavedClinic.objects.get(user=self.user)
        self.assertEqual(clinic.name, "Test Clinic")
        self.assertEqual(clinic.external_place_id, "test123")

    def test_remove_clinic_requires_authentication(self):
        """Test that remove clinic endpoint requires authentication."""
        clinic = SavedClinic.objects.create(
            user=self.user,
            name="Test Clinic",
            address_line="123 Main St",
            city="New York",
            latitude=40.7128,
            longitude=-74.0060,
        )
        response = self.client.post(
            reverse("locator:remove_clinic"),
            data=json.dumps({"clinic_id": clinic.id}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_remove_clinic_not_found(self):
        """Test removing non-existent clinic."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("locator:remove_clinic"),
            data=json.dumps({"clinic_id": 99999}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertIn("error", data)

    def test_remove_clinic_success(self):
        """Test successful clinic removal."""
        self.client.login(username="testuser", password="testpass123")
        clinic = SavedClinic.objects.create(
            user=self.user,
            name="Test Clinic",
            address_line="123 Main St",
            city="New York",
            latitude=40.7128,
            longitude=-74.0060,
        )
        response = self.client.post(
            reverse("locator:remove_clinic"),
            data=json.dumps({"clinic_id": clinic.id}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["success"])

        # Verify clinic was deleted
        with self.assertRaises(SavedClinic.DoesNotExist):
            SavedClinic.objects.get(id=clinic.id)


class SavedClinicModelTests(TestCase):
    """Test SavedClinic model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_create_saved_clinic(self):
        """Test creating a saved clinic."""
        clinic = SavedClinic.objects.create(
            user=self.user,
            name="Test Clinic",
            address_line="123 Main St",
            city="New York",
            latitude=40.7128,
            longitude=-74.0060,
        )
        self.assertEqual(clinic.name, "Test Clinic")
        self.assertEqual(clinic.user, self.user)

    def test_latitude_validation(self):
        """Test latitude validation."""
        clinic = SavedClinic(
            user=self.user,
            name="Test",
            address_line="123 Main St",
            latitude=95,  # Invalid
            longitude=-74,
        )
        with self.assertRaises(Exception):
            clinic.full_clean()

    def test_longitude_validation(self):
        """Test longitude validation."""
        clinic = SavedClinic(
            user=self.user,
            name="Test",
            address_line="123 Main St",
            latitude=40.7,
            longitude=200,  # Invalid
        )
        with self.assertRaises(Exception):
            clinic.full_clean()


class GooglePlacesServiceTests(TestCase):
    """Test GooglePlacesService (without actual API calls)."""

    def test_nearby_location_to_dict(self):
        """Test NearbyLocation dataclass serialization."""
        location = NearbyLocation(
            place_id="test123",
            name="Test Clinic",
            address="123 Main St",
            latitude=40.7128,
            longitude=-74.0060,
            distance_meters=500,
            phone="555-1234",
            website="https://test.com",
            rating=4.5,
        )
        data = location.to_dict()
        self.assertEqual(data["place_id"], "test123")
        self.assertEqual(data["name"], "Test Clinic")
        self.assertEqual(data["distance_meters"], 500)
        self.assertIsInstance(data, dict)

    def test_haversine_distance_calculation(self):
        """Test Haversine distance calculation."""
        # New York to Los Angeles (approx 3944 km)
        distance = GooglePlacesService._haversine_distance(40.7128, -74.0060, 34.0522, -118.2437)
        # Should be approximately 3944000 meters
        self.assertGreater(distance, 3900000)
        self.assertLess(distance, 4000000)

    def test_haversine_zero_distance(self):
        """Test Haversine distance for same point."""
        distance = GooglePlacesService._haversine_distance(40.7128, -74.0060, 40.7128, -74.0060)
        self.assertLess(distance, 100)  # Should be near zero

