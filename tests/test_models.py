"""Test Pydantic models."""

import pytest
from pydantic import ValidationError

from app.models.schemas import (
    Patient,
    Lab,
    Lifestyle,
    Assessment,
    CategoryReport,
    MedicalReport,
)


def test_patient_valid():
    """Test creating valid patient."""
    patient = Patient(name="John Doe", age=35, sex="male")
    assert patient.name == "John Doe"
    assert patient.age == 35
    assert patient.sex == "male"


def test_patient_invalid_missing_field():
    """Test patient with missing required field."""
    with pytest.raises(ValidationError):
        Patient(name="John Doe", age=35)  # Missing sex


def test_lab_valid():
    """Test creating valid lab result."""
    lab = Lab(
        category="biochemistry",
        test_name="Sodium",
        value="140",
        unit="mmol/L",
        reference_range="135-145",
        flag="normal"
    )
    assert lab.category == "biochemistry"
    assert lab.test_name == "Sodium"


def test_lifestyle_valid():
    """Test creating valid lifestyle."""
    lifestyle = Lifestyle(
        smoking="Never smoked",
        alcohol="None",
        diet="Balanced",
        physical_activity="Moderate"
    )
    assert lifestyle.smoking == "Never smoked"


def test_assessment_valid():
    """Test creating valid assessment."""
    lifestyle = Lifestyle(
        smoking="Never",
        alcohol="None",
        diet="Good",
        physical_activity="Active"
    )
    assessment = Assessment(
        summary="Test summary",
        family_history="None",
        lifestyle=lifestyle
    )
    assert assessment.summary == "Test summary"
    assert assessment.lifestyle.smoking == "Never"


def test_category_report_valid():
    """Test creating valid category report."""
    report = CategoryReport(
        category="weight_management",
        text="This is a friendly report with [links](https://example.com).",
        sources=["https://example.com", "https://example.org"]
    )
    assert report.category == "weight_management"
    assert len(report.sources) == 2


def test_medical_report_minimal():
    """Test creating minimal medical report."""
    report = MedicalReport(
        patient=Patient(name="Test", age=30, sex="F"),
        labs=[],
        assessment=Assessment(
            summary="Test",
            family_history="None",
            lifestyle=Lifestyle(
                smoking="No",
                alcohol="No",
                diet="Good",
                physical_activity="Yes"
            )
        ),
        plan=[],
        red_flags=[],
        resources_table=[],
        disclaimer="Test disclaimer"
    )
    assert report.patient.name == "Test"
    assert report.category_reports == []  # Optional field with default


def test_medical_report_with_category_reports():
    """Test medical report with category reports."""
    report = MedicalReport(
        patient=Patient(name="Test", age=30, sex="F"),
        labs=[],
        assessment=Assessment(
            summary="Test",
            family_history="None",
            lifestyle=Lifestyle(
                smoking="No",
                alcohol="No",
                diet="Good",
                physical_activity="Yes"
            )
        ),
        plan=[],
        red_flags=[],
        resources_table=[],
        category_reports=[
            CategoryReport(
                category="test",
                text="Test report",
                sources=["https://example.com"]
            )
        ],
        disclaimer="Test"
    )
    assert len(report.category_reports) == 1
    assert report.category_reports[0].category == "test"
