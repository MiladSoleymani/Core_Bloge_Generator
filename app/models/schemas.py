"""Pydantic models for medical report generation."""

from typing import List, Optional
from datetime import datetime
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


# RabbitMQ Message Schemas

class ReportGenerationRequest(BaseModel):
    """RabbitMQ request message for report generation."""

    request_id: str = Field(description="Unique request identifier")
    user_id: str = Field(description="User identifier")
    patient: Patient
    labs: List[Lab]
    cvd_summary: Optional[CVDSummary] = None
    assessment: Assessment
    plan: List[PlanItem]
    red_flags: List[RedFlag]
    resources_table: List[Resource]
    disclaimer: str = "This report is based on the provided clinical data and risk calculator outputs. It is intended for informational purposes and should not replace professional medical advice. Please consult your healthcare provider for personalized recommendations."


class ReportGenerationResponse(BaseModel):
    """RabbitMQ response message for report generation."""

    request_id: str = Field(description="Original request identifier")
    user_id: str = Field(description="User identifier")
    report_id: str = Field(description="Generated report identifier")
    status: str = Field(description="Status: success, failed")
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# MongoDB Storage Schemas

class StoredUser(BaseModel):
    """User information stored in MongoDB."""

    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class StoredReport(BaseModel):
    """Medical report stored in MongoDB."""

    report_id: str
    user_id: str
    report_data: MedicalReport
    json_content: dict
    markdown_content: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    generation_time_seconds: Optional[float] = None
    tokens_used: Optional[int] = None
    estimated_cost: Optional[float] = None
