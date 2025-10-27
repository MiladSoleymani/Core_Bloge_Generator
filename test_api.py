"""Simple test script for the API."""

import json
import requests
from pathlib import Path

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    return response.status_code == 200


def test_import_kb():
    """Test knowledge base import."""
    print("Testing knowledge base import...")
    response = requests.post(f"{BASE_URL}/api/knowledge-base/import")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    return response.status_code == 200


def test_get_categories():
    """Test getting categories."""
    print("Testing get categories...")
    response = requests.get(f"{BASE_URL}/api/knowledge-base/categories")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    return response.status_code == 200


def test_generate_report():
    """Test report generation with sample data."""
    print("Testing report generation...")

    # Load sample report data
    sample_file = Path("data/sample_reports/Kushagra mandwal.json")

    if not sample_file.exists():
        print(f"Error: Sample file not found at {sample_file}")
        return False

    with open(sample_file, "r") as f:
        data = json.load(f)

    # Send request
    response = requests.post(
        f"{BASE_URL}/api/generate-report",
        json=data,
        timeout=120,  # 2 minutes timeout for AI generation
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        report_id = result.get("report_id")
        print(f"Report ID: {report_id}")
        print(f"Status: {result.get('status')}")
        print(f"Categories generated: {len(result.get('report', {}).get('category_reports', []))}")

        # Save the full report to file for review
        output_file = Path("test_output_report.json")
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Full report saved to: {output_file}\n")

        return True, report_id
    else:
        print(f"Error: {response.text}\n")
        return False, None


def test_get_report(report_id):
    """Test retrieving a report."""
    print(f"Testing get report for ID: {report_id}...")
    response = requests.get(f"{BASE_URL}/api/reports/{report_id}")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Report retrieved successfully")
        print(f"Patient: {result['patient']['name']}")
        print(f"Categories: {len(result['category_reports'])}\n")
        return True
    else:
        print(f"Error: {response.text}\n")
        return False


def test_get_markdown(report_id):
    """Test retrieving markdown version."""
    print(f"Testing get markdown for ID: {report_id}...")
    response = requests.get(f"{BASE_URL}/api/reports/{report_id}/markdown")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        markdown = result.get("content", "")
        print(f"Markdown length: {len(markdown)} characters")

        # Save markdown to file
        output_file = Path("test_output_report.md")
        with open(output_file, "w") as f:
            f.write(markdown)
        print(f"Markdown saved to: {output_file}\n")
        return True
    else:
        print(f"Error: {response.text}\n")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("API Test Suite")
    print("=" * 60 + "\n")

    try:
        # Test 1: Health check
        if not test_health():
            print("Health check failed. Is the server running?")
            return

        # Test 2: Import knowledge base
        if not test_import_kb():
            print("Knowledge base import failed.")
            return

        # Test 3: Get categories
        if not test_get_categories():
            print("Get categories failed.")
            return

        # Test 4: Generate report
        print("=" * 60)
        print("Generating report (this may take 30-60 seconds)...")
        print("=" * 60 + "\n")

        result = test_generate_report()
        if isinstance(result, tuple):
            success, report_id = result
            if not success:
                print("Report generation failed.")
                return
        else:
            print("Report generation failed.")
            return

        # Test 5: Get report
        if not test_get_report(report_id):
            print("Get report failed.")
            return

        # Test 6: Get markdown
        if not test_get_markdown(report_id):
            print("Get markdown failed.")
            return

        print("=" * 60)
        print("All tests passed!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the server.")
        print("Make sure the server is running: python -m app.main")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")


if __name__ == "__main__":
    main()
