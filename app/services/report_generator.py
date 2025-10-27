"""Report generation service using OpenAI and LangChain."""

import os
from typing import List, Dict
from datetime import datetime
import uuid

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser

from app.models.schemas import CategoryReport, CategoryReportItem, MedicalReport
from app.core.config import get_settings

settings = get_settings()


class ReportGeneratorService:
    """Service for generating medical reports using AI."""

    def __init__(self):
        """Initialize the service."""
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,
        )
        self.parser = JsonOutputParser(pydantic_object=CategoryReport)

    async def generate_category_report(
        self, category_content: str, category: str
    ) -> Dict:
        """Generate a friendly report for a specific category.

        Args:
            category_content: Aggregated content from knowledge base for the category
            category: Category name (e.g., 'weight_management', 'blood_pressure')

        Returns:
            Dictionary with category, text, and sources
        """
        system_message = SystemMessage(
            content="""You are a helpful health information assistant.
Create a friendly, one-page report summarizing the provided content.
Keep the tone warm and encouraging.
Include inline links in the text using markdown format [text](url).
Also provide a separate list of all source URLs at the end."""
        )

        human_message = HumanMessage(
            content=f"""Based on the following content about {category},
create a one-page friendly summary report.
Include inline source links in markdown format throughout the text.
Extract and list all source URLs separately.

Content:
{category_content}

{self.parser.get_format_instructions()}"""
        )

        response = self.llm.invoke([system_message, human_message])
        return self.parser.parse(response.content)

    async def generate_reports_for_categories(
        self, categories_content: Dict[str, str]
    ) -> List[CategoryReportItem]:
        """Generate reports for multiple categories.

        Args:
            categories_content: Dict mapping category names to their aggregated content

        Returns:
            List of CategoryReportItem objects
        """
        reports = []

        for category, content in categories_content.items():
            if not content:
                continue

            print(f"Generating report for category: {category}")
            report_dict = await self.generate_category_report(content, category)
            report = CategoryReportItem(**report_dict)
            reports.append(report)

        return reports

    def generate_markdown(self, report: MedicalReport) -> str:
        """Generate markdown format of the medical report.

        Args:
            report: Complete medical report

        Returns:
            Markdown-formatted report as string
        """
        md_parts = []

        # Header
        md_parts.append(f"# Medical Report: {report.patient.name}\n\n")
        md_parts.append(f"**Date Generated:** {datetime.now().strftime('%Y-%m-%d')}\n\n")

        # Patient Information
        md_parts.append("## Patient Information\n\n")
        md_parts.append(f"- **Name:** {report.patient.name}\n")
        md_parts.append(f"- **Age:** {report.patient.age}\n")
        md_parts.append(f"- **Sex:** {report.patient.sex}\n\n")

        # CVD Summary (if exists)
        if report.cvd_summary:
            md_parts.append("## Cardiovascular Risk Summary\n\n")
            md_parts.append(f"**Risk Level:** {report.cvd_summary.risk_level.upper()}\n\n")
            md_parts.append(f"**5-Year Risk:** {report.cvd_summary.five_year_risk_percent}%\n\n")
            md_parts.append(f"**Interpretation:** {report.cvd_summary.interpretation}\n\n")

            if report.cvd_summary.modifiable_risk_factors:
                md_parts.append("**Modifiable Risk Factors:**\n\n")
                for factor in report.cvd_summary.modifiable_risk_factors:
                    md_parts.append(f"- {factor}\n")
                md_parts.append("\n")

            if report.cvd_summary.risk_reduction_advice:
                md_parts.append("**Risk Reduction Advice:**\n\n")
                for advice in report.cvd_summary.risk_reduction_advice:
                    md_parts.append(f"- {advice}\n")
                md_parts.append("\n")

        # Assessment
        md_parts.append("## Assessment\n\n")
        md_parts.append(f"{report.assessment.summary}\n\n")

        md_parts.append("### Lifestyle\n\n")
        md_parts.append(f"- **Smoking:** {report.assessment.lifestyle.smoking}\n")
        md_parts.append(f"- **Alcohol:** {report.assessment.lifestyle.alcohol}\n")
        md_parts.append(f"- **Diet:** {report.assessment.lifestyle.diet}\n")
        md_parts.append(f"- **Physical Activity:** {report.assessment.lifestyle.physical_activity}\n\n")

        # Red Flags
        if report.red_flags:
            md_parts.append("## Red Flags\n\n")
            for flag in report.red_flags:
                md_parts.append(f"### {flag.symptom}\n\n")
                md_parts.append(f"{flag.note}\n\n")

        # Treatment Plan
        if report.plan:
            md_parts.append("## Treatment Plan\n\n")
            for i, item in enumerate(report.plan, 1):
                md_parts.append(f"{i}. {item.advice}\n")
            md_parts.append("\n")

        # Category Reports (Detailed Health Information)
        if report.category_reports:
            md_parts.append("## Detailed Health Information Guides\n\n")
            for cat_report in report.category_reports:
                md_parts.append(f"### {cat_report.category.replace('_', ' ').title()}\n\n")
                md_parts.append(f"{cat_report.text}\n\n")

                if cat_report.sources:
                    md_parts.append("**Sources:**\n\n")
                    for source in cat_report.sources:
                        md_parts.append(f"- {source}\n")
                    md_parts.append("\n")

                md_parts.append("---\n\n")

        # Resources
        if report.resources_table:
            md_parts.append("## Additional Resources\n\n")
            # Group by category
            resources_by_category = {}
            for resource in report.resources_table:
                if resource.category not in resources_by_category:
                    resources_by_category[resource.category] = []
                resources_by_category[resource.category].append(resource)

            for category, resources in resources_by_category.items():
                md_parts.append(f"### {category.replace('_', ' ').title()}\n\n")
                for resource in resources:
                    md_parts.append(f"- [{resource.title}]({resource.url})\n")
                md_parts.append("\n")

        # Disclaimer
        md_parts.append("---\n\n")
        md_parts.append("## Disclaimer\n\n")
        md_parts.append(f"{report.disclaimer}\n")

        return "".join(md_parts)
