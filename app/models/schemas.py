"""Pydantic models for medical report generation."""

from typing import List, Optional
from pydantic import BaseModel, Field


class Patient(BaseModel):
    """Patient information."""

    name: str
    age: int
    sex: str


class Lab(BaseModel):
    """Laboratory test result."""

    category: str
    test_name: str
    value: str
    unit: str
    reference_range: str
    flag: str


class CVDSummary(BaseModel):
    """Cardiovascular disease risk summary."""

    five_year_risk_percent: float
    risk_level: str
    interpretation: str
    modifiable_risk_factors: List[str]
    risk_reduction_advice: List[str]


class Lifestyle(BaseModel):
    """Lifestyle information."""

    smoking: str
    alcohol: str
    diet: str
    physical_activity: str


class Assessment(BaseModel):
    """Clinical assessment."""

    summary: str
    family_history: str
    lifestyle: Lifestyle


class PlanItem(BaseModel):
    """Treatment plan item."""

    advice: str
    kb_resource_id: str


class RedFlag(BaseModel):
    """Clinical red flag."""

    symptom: str
    note: str


class Resource(BaseModel):
    """Reference resource."""

    category: str
    title: str
    url: str


class CategoryReportItem(BaseModel):
    """Generated category report."""

    category: str
    text: str
    sources: List[str]


class MedicalReport(BaseModel):
    """Complete medical report."""

    patient: Patient
    labs: List[Lab]
    cvd_summary: Optional[CVDSummary] = None
    assessment: Assessment
    plan: List[PlanItem]
    red_flags: List[RedFlag]
    resources_table: List[Resource]
    category_reports: Optional[List[CategoryReportItem]] = Field(default_factory=list)
    disclaimer: str


class KnowledgeBaseItem(BaseModel):
    """Knowledge base metadata item."""

    file_name: str
    id: str
    title: str
    category: str
    applies_to: List[str]
    summary_length_words: int
    source_url: str
    verified_source: bool
    last_updated: str
    status: str


class CategoryReport(BaseModel):
    """AI-generated category report."""

    category: str = Field(description="The category of the report")
    text: str = Field(
        description="The one-page friendly report text with inline source links"
    )
    sources: List[str] = Field(description="List of source URLs used")


class ReportRequest(BaseModel):
    """Request to generate a medical report."""

    patient: Patient
    labs: List[Lab]
    cvd_summary: Optional[CVDSummary] = None
    assessment: Assessment
    plan: List[PlanItem]
    red_flags: List[RedFlag]
    resources_table: List[Resource]
    disclaimer: str = "This report is based on the provided clinical data and risk calculator outputs. It is intended for informational purposes and should not replace professional medical advice. Please consult your healthcare provider for personalized recommendations."


class JobStatusResponse(BaseModel):
    """Async job status response."""

    job_id: str
    status: str  # queued, processing, completed, failed
    progress: Optional[int] = None  # percentage
    result: Optional[dict] = None
    error_message: Optional[str] = None


class GenerateReportResponse(BaseModel):
    """Response from report generation."""

    report_id: str
    status: str
    report: Optional[MedicalReport] = None
