from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from accounts.models import UserProfile


@dataclass(frozen=True)
class RecommendationResult:
    vitamin_name: str
    reason: str
    food_sources: list[str]
    suggested_frequency: str
    caution_note: str
    priority_label: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RecommendationEngine:
    """Rule-based recommendation generator for VitaminSHE."""

    PRIORITY_HIGH = "high"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_LOW = "low"

    def generate(
        self,
        profile: UserProfile,
        *,
        sunlight_exposure: str = "moderate",
        fatigue: bool = False,
        iron_deficiency_history: bool = False,
        vitamin_d_deficiency_history: bool = False,
        health_goals: list[str] | None = None,
        allergies_or_restrictions: list[str] | None = None,
    ) -> list[RecommendationResult]:
        if not isinstance(profile, UserProfile):
            raise TypeError("profile must be a UserProfile instance")

        sunlight = self._normalize_sunlight(sunlight_exposure)
        goals = self._normalize_tags(health_goals)
        restrictions = self._normalize_tags(allergies_or_restrictions)
        diet_tokens = self._normalize_tags([profile.dietary_preferences])
        restrictions |= diet_tokens

        results: dict[str, RecommendationResult] = {}

        def add_result(result: RecommendationResult) -> None:
            existing = results.get(result.vitamin_name)
            if existing is None:
                results[result.vitamin_name] = result
                return
            if self._priority_rank(result.priority_label) > self._priority_rank(existing.priority_label):
                results[result.vitamin_name] = result

        if profile.is_pregnant:
            add_result(
                RecommendationResult(
                    vitamin_name="Folate (Vitamin B9)",
                    reason="Pregnancy increases folate needs for fetal neural development.",
                    food_sources=self._filter_foods(
                        ["lentils", "spinach", "asparagus", "fortified cereals"],
                        restrictions,
                    ),
                    suggested_frequency="Daily",
                    caution_note="Do not exceed prenatal supplement dose unless advised by a clinician.",
                    priority_label=self.PRIORITY_HIGH,
                )
            )

            add_result(
                RecommendationResult(
                    vitamin_name="Iron",
                    reason="Pregnancy can increase blood volume and iron requirements.",
                    food_sources=self._filter_foods(
                        ["lean red meat", "lentils", "spinach", "beans"],
                        restrictions,
                    ),
                    suggested_frequency="Daily",
                    caution_note="Take iron away from calcium-rich meals when possible for better absorption.",
                    priority_label=self.PRIORITY_HIGH,
                )
            )

        if iron_deficiency_history or fatigue:
            add_result(
                RecommendationResult(
                    vitamin_name="Iron",
                    reason="Fatigue and prior iron deficiency can indicate ongoing iron support needs.",
                    food_sources=self._filter_foods(
                        ["lean red meat", "lentils", "chickpeas", "pumpkin seeds"],
                        restrictions,
                    ),
                    suggested_frequency="5-7 days/week through food; supplements per clinician advice",
                    caution_note="Pair with vitamin C foods for absorption; avoid self-medicating high-dose iron.",
                    priority_label=self.PRIORITY_HIGH if iron_deficiency_history else self.PRIORITY_MEDIUM,
                )
            )

        if vitamin_d_deficiency_history or sunlight == "low":
            add_result(
                RecommendationResult(
                    vitamin_name="Vitamin D",
                    reason="Low sunlight or prior deficiency raises risk of low vitamin D status.",
                    food_sources=self._filter_foods(
                        ["salmon", "sardines", "egg yolks", "fortified milk"],
                        restrictions,
                    ),
                    suggested_frequency="Daily intake; sunlight exposure 10-20 min when feasible",
                    caution_note="High-dose vitamin D should be based on lab follow-up.",
                    priority_label=self.PRIORITY_HIGH if vitamin_d_deficiency_history else self.PRIORITY_MEDIUM,
                )
            )

        if fatigue:
            add_result(
                RecommendationResult(
                    vitamin_name="Vitamin B12",
                    reason="Fatigue may be associated with low B12 intake in some diets.",
                    food_sources=self._filter_foods(
                        ["fish", "eggs", "dairy", "fortified nutritional yeast"],
                        restrictions,
                    ),
                    suggested_frequency="Daily or most days each week",
                    caution_note="If symptoms persist, consider lab testing before long-term high-dose supplements.",
                    priority_label=self.PRIORITY_MEDIUM,
                )
            )

        if any(tag in goals for tag in {"bone health", "bone", "osteoporosis prevention"}):
            add_result(
                RecommendationResult(
                    vitamin_name="Calcium + Vitamin D",
                    reason="Bone-health goals benefit from paired calcium and vitamin D intake.",
                    food_sources=self._filter_foods(
                        ["yogurt", "fortified plant milk", "tofu", "sardines"],
                        restrictions,
                    ),
                    suggested_frequency="Daily",
                    caution_note="Split calcium doses for better absorption and hydration.",
                    priority_label=self.PRIORITY_MEDIUM,
                )
            )

        if any(tag in goals for tag in {"energy", "energy support", "reduce fatigue"}):
            add_result(
                RecommendationResult(
                    vitamin_name="B-Complex (B6, B12, Folate)",
                    reason="Energy-support goals align with adequate B-vitamin intake.",
                    food_sources=self._filter_foods(
                        ["whole grains", "eggs", "leafy greens", "legumes"],
                        restrictions,
                    ),
                    suggested_frequency="Daily",
                    caution_note="Balanced food-first intake is preferred over megadose supplements.",
                    priority_label=self.PRIORITY_MEDIUM,
                )
            )

        if any(tag in diet_tokens for tag in {"vegetarian", "vegan"}):
            add_result(
                RecommendationResult(
                    vitamin_name="Vitamin B12",
                    reason="Plant-forward diets can be low in natural vitamin B12 sources.",
                    food_sources=self._filter_foods(
                        ["fortified plant milk", "fortified cereals", "nutritional yeast"],
                        restrictions,
                    ),
                    suggested_frequency="Daily or fortified intake multiple times weekly",
                    caution_note="Consider periodic B12 monitoring if fully vegan.",
                    priority_label=self.PRIORITY_HIGH if "vegan" in diet_tokens else self.PRIORITY_MEDIUM,
                )
            )

        if not results:
            add_result(
                RecommendationResult(
                    vitamin_name="General Multinutrient Food Pattern",
                    reason="No high-risk triggers detected; maintain broad nutrient coverage through diet.",
                    food_sources=self._filter_foods(
                        ["leafy greens", "beans", "nuts", "seasonal fruit", "fatty fish"],
                        restrictions,
                    ),
                    suggested_frequency="Daily varied meals",
                    caution_note="Reassess with lab data or symptom changes.",
                    priority_label=self.PRIORITY_LOW,
                )
            )

        return sorted(results.values(), key=lambda item: self._priority_rank(item.priority_label), reverse=True)

    @staticmethod
    def _normalize_sunlight(value: str) -> str:
        sunlight = (value or "moderate").strip().lower()
        if sunlight not in {"low", "moderate", "high"}:
            raise ValueError("sunlight_exposure must be one of: low, moderate, high")
        return sunlight

    @staticmethod
    def _normalize_tags(values: list[str] | None) -> set[str]:
        if not values:
            return set()

        tags: set[str] = set()
        for raw in values:
            if not raw:
                continue
            parts = [part.strip().lower() for part in str(raw).replace(";", ",").split(",")]
            tags.update({part for part in parts if part})
        return tags

    @staticmethod
    def _filter_foods(food_sources: list[str], restrictions: set[str]) -> list[str]:
        filtered = list(food_sources)

        if any(tag in restrictions for tag in {"vegan", "vegetarian"}):
            filtered = [
                food
                for food in filtered
                if food not in {"lean red meat", "sardines", "salmon", "fish"}
            ]

        if "lactose intolerant" in restrictions or "dairy-free" in restrictions:
            filtered = [food for food in filtered if "milk" not in food and food != "yogurt" and food != "dairy"]

        if "nut allergy" in restrictions:
            filtered = [food for food in filtered if "nut" not in food]

        return filtered or ["Discuss personalized alternatives with a registered dietitian."]

    @staticmethod
    def _priority_rank(priority: str) -> int:
        ranks = {
            RecommendationEngine.PRIORITY_LOW: 1,
            RecommendationEngine.PRIORITY_MEDIUM: 2,
            RecommendationEngine.PRIORITY_HIGH: 3,
        }
        return ranks.get(priority, 0)


def generate_recommendations(
    profile: UserProfile,
    *,
    diet: str | None = None,
    pregnancy_status: bool | None = None,
    sunlight_exposure: str = "moderate",
    fatigue: bool = False,
    iron_deficiency_history: bool = False,
    vitamin_d_deficiency_history: bool = False,
    health_goals: list[str] | None = None,
    allergies_restrictions: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Convenience function returning serializable recommendation dictionaries."""
    if diet is not None:
        profile.dietary_preferences = diet
    if pregnancy_status is not None:
        profile.is_pregnant = pregnancy_status

    engine = RecommendationEngine()
    results = engine.generate(
        profile,
        sunlight_exposure=sunlight_exposure,
        fatigue=fatigue,
        iron_deficiency_history=iron_deficiency_history,
        vitamin_d_deficiency_history=vitamin_d_deficiency_history,
        health_goals=health_goals,
        allergies_or_restrictions=allergies_restrictions,
    )
    return [result.to_dict() for result in results]


# Vitamin calculation functions integrated from standalone VitaminSHE.py
from datetime import datetime
from .vitamin_data import VITAMIN_REQUIREMENTS, VITAMIN_INFO


def calculate_age_from_date(date_of_birth):
    """Calculate age in years from date of birth."""
    if not date_of_birth:
        return None
    today = datetime.now().date()
    age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    return age


def compute_age_range(age, is_pregnant=False, is_breastfeeding=False):
    """
    Determine the age range category for vitamin requirements.
    
    Args:
        age: User's age in years
        is_pregnant: Boolean indicating pregnancy status
        is_breastfeeding: Boolean indicating breastfeeding status
    
    Returns:
        str: Age range category
    """
    if age is None or age < 0:
        return None
    
    # Factors in Pregnancy and Lactation
    if is_pregnant or is_breastfeeding:
        # If both pregnant and lactating, simulation assumes lactation label
        if is_pregnant and is_breastfeeding:
            return "Lact. <= 18" if age <= 18 else "Lact. 19+"
        
        # Checks age and pregnancy status
        if is_pregnant:
            return "Preg. <= 18" if age <= 18 else "Preg. 19+"
        
        # Checks age and lactation status
        if is_breastfeeding:
            return "Lact. <= 18" if age <= 18 else "Lact. 19+"
    
    # Non-pregnant/non-breastfeeding age ranges
    if age < 1:
        return "Infant"
    elif 1 <= age <= 3:
        return "1-3"
    elif 4 <= age <= 8:
        return "4-8"
    elif 9 <= age <= 13:
        return "9-13"
    elif 14 <= age <= 18:
        return "14-18"
    elif 19 <= age <= 30:
        return "19-30"
    elif 31 <= age <= 50:
        return "31-50"
    elif 51 <= age <= 70:
        return "51-70"
    else:  # 71+
        return "71+"


def get_vitamin_recommendations(age, is_pregnant=False, is_breastfeeding=False):
    """
    Calculate personalized vitamin and mineral recommendations for a user.
    
    Args:
        age: User's age in years
        is_pregnant: Boolean indicating pregnancy status
        is_breastfeeding: Boolean indicating breastfeeding status
    
    Returns:
        dict: Dictionary with vitamin/mineral names and their daily requirements
    """
    age_range = compute_age_range(age, is_pregnant, is_breastfeeding)
    
    if not age_range:
        return {}
    
    recommendations = {}
    for vitamin_name, requirements in VITAMIN_REQUIREMENTS.items():
        try:
            recommendations[vitamin_name] = requirements.get(age_range, None)
        except (KeyError, TypeError):
            recommendations[vitamin_name] = None
    
    return recommendations


def get_vitamin_details(vitamin_id):
    """Get detailed information about a specific vitamin."""
    return VITAMIN_INFO.get(vitamin_id, {})


def get_all_vitamins_info():
    """Get information about all vitamins and minerals."""
    return VITAMIN_INFO
