
from math import floor
from .models import Donation, EvaluationSettings


def evaluate_donation(
    donation: Donation,
    settings: EvaluationSettings | None = None
):
    if settings is None:
        settings = EvaluationSettings()

    # Demonstration rates, NOT verified FGT data
    default_rates = {
        "Good": 0.85,
        "Fair": 0.60,
        "Poor": 0.25
    }

    expected_rate = (
        settings.expected_rate
        if settings.expected_rate is not None
        else default_rates[donation.condition]
    )

    # Keep the low and high scenarios around the expected rate
    low_rate = min(settings.conservative_rate, expected_rate)
    high_rate = max(settings.optimistic_rate, expected_rate)

    collection_expense = (
        settings.collection_expense
        if settings.collection_expense is not None
        else donation.pickup_cost
    )

    def calculate_scenario(rate):
        usable = floor(donation.quantity * rate)

        revenue = (
            usable * settings.sale_price
            + settings.pickup_fee_revenue
        )

        parts = usable * settings.parts_cost
        labour = (
            usable
            * settings.labour_hours
            * settings.hourly_labour_value
        )

        total_cost = parts + labour + collection_expense
        contribution = revenue - total_cost

        total_hours = usable * settings.labour_hours

        contribution_per_hour = (
            contribution / total_hours
            if total_hours > 0
            else None
        )

        return {
            "refurbishment_rate": round(rate, 3),
            "estimated_usable_devices": usable,
            "estimated_revenue": round(revenue, 2),
            "estimated_cost": round(total_cost, 2),
            "estimated_contribution": round(contribution, 2),
            "estimated_labour_hours": round(total_hours, 2),
            "contribution_per_hour": (
                round(contribution_per_hour, 2)
                if contribution_per_hour is not None
                else None
            )
        }

    scenarios = {
        "conservative": calculate_scenario(low_rate),
        "expected": calculate_scenario(expected_rate),
        "optimistic": calculate_scenario(high_rate)
    }

    expected = scenarios["expected"]

    warnings = []

    if donation.condition == "Poor":
        warnings.append(
            "Poor condition may reduce refurbishment yield."
        )

    if not donation.uniform_models:
        warnings.append(
            "Mixed models may require additional repair time."
        )

    if donation.device_type == "Desktop":
        warnings.append(
            "Verify desktop suitability and storage needs."
        )

    if expected["estimated_contribution"] < 0:
        warnings.append(
            "Expected contribution is negative."
        )

    if (
        expected["estimated_labour_hours"]
        > settings.available_labour_hours
    ):
        warnings.append(
            "Estimated labour exceeds available capacity."
        )

    if donation.quantity > settings.available_storage_slots:
        warnings.append(
            "Donation quantity exceeds available storage slots."
        )

    warnings.append(
        "All financial figures are hypothetical and require "
        "validation with Free Geek Toronto."
    )

    return {
        "company_name": donation.company_name,
        "device_type": donation.device_type,
        "quantity": donation.quantity,
        "condition": donation.condition,
        "scenarios": scenarios,
        "estimated_usable_devices":
            expected["estimated_usable_devices"],
        "estimated_revenue":
            expected["estimated_revenue"],
        "estimated_cost":
            expected["estimated_cost"],
        "estimated_contribution":
            expected["estimated_contribution"],
        "estimated_labour_hours":
            expected["estimated_labour_hours"],
        "contribution_per_hour":
            expected["contribution_per_hour"],
        "warnings": warnings,
        "requires_staff_review": True,
        "is_illustrative": True
    }
