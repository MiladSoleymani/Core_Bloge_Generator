"""
Check reports and users in MongoDB database.

This script allows you to view stored reports and users from the MongoDB database.

Usage:
    python scripts/check_database.py
    python scripts/check_database.py --list-reports
    python scripts/check_database.py --report-id <id>
    python scripts/check_database.py --user-id <id>
"""

import asyncio
import argparse
import json
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import get_settings

settings = get_settings()


async def connect_db():
    """Connect to MongoDB."""
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]
    return client, db


async def list_users(db):
    """List all users in database."""
    print("\n" + "="*60)
    print("USERS IN DATABASE")
    print("="*60)

    users = await db.users.find().to_list(length=100)

    if not users:
        print("No users found.")
        return

    for user in users:
        print(f"\nUser ID: {user['user_id']}")
        print(f"Created: {user['created_at']}")
        print(f"Updated: {user['updated_at']}")

    print(f"\nTotal users: {len(users)}")


async def list_reports(db, user_id=None):
    """List all reports in database."""
    print("\n" + "="*60)
    print("REPORTS IN DATABASE")
    print("="*60)

    query = {}
    if user_id:
        query['user_id'] = user_id
        print(f"Filtering by user_id: {user_id}")

    reports = await db.medical_reports.find(query).sort("created_at", -1).to_list(length=100)

    if not reports:
        print("No reports found.")
        return

    for report in reports:
        print(f"\n{'─'*60}")
        print(f"Report ID: {report['report_id']}")
        print(f"User ID: {report['user_id']}")
        print(f"Patient: {report['report_data']['patient']['name']}")
        print(f"Age: {report['report_data']['patient']['age']}")
        print(f"Sex: {report['report_data']['patient']['sex']}")
        print(f"Created: {report['created_at']}")

        if 'generation_time_seconds' in report:
            print(f"Generation Time: {report['generation_time_seconds']:.2f}s")

        # Show categories
        if 'category_reports' in report['report_data']:
            categories = [cr['category'] for cr in report['report_data']['category_reports']]
            print(f"Categories: {', '.join(categories)}")

    print(f"\n{'='*60}")
    print(f"Total reports: {len(reports)}")


async def get_report_by_id(db, report_id):
    """Get specific report by ID."""
    print("\n" + "="*60)
    print("REPORT DETAILS")
    print("="*60)

    report = await db.medical_reports.find_one({"report_id": report_id})

    if not report:
        print(f"Report not found: {report_id}")
        return

    print(f"\nReport ID: {report['report_id']}")
    print(f"User ID: {report['user_id']}")
    print(f"Created: {report['created_at']}")

    if 'generation_time_seconds' in report:
        print(f"Generation Time: {report['generation_time_seconds']:.2f}s")

    # Patient info
    patient = report['report_data']['patient']
    print(f"\nPatient:")
    print(f"  Name: {patient['name']}")
    print(f"  Age: {patient['age']}")
    print(f"  Sex: {patient['sex']}")

    # Assessment
    if 'assessment' in report['report_data']:
        assessment = report['report_data']['assessment']
        print(f"\nAssessment:")
        print(f"  Summary: {assessment['summary'][:100]}...")

    # CVD Summary
    if report['report_data'].get('cvd_summary'):
        cvd = report['report_data']['cvd_summary']
        print(f"\nCVD Risk:")
        print(f"  Risk Level: {cvd['risk_level']}")
        print(f"  5-Year Risk: {cvd['five_year_risk_percent']}%")

    # Category reports
    if 'category_reports' in report['report_data']:
        print(f"\nCategory Reports:")
        for cr in report['report_data']['category_reports']:
            print(f"  - {cr['category']}: {len(cr['text'])} chars, {len(cr['sources'])} sources")

    # Show if markdown is available
    if report.get('markdown_content'):
        print(f"\nMarkdown: Available ({len(report['markdown_content'])} chars)")

    print("\n" + "="*60)


async def get_report_markdown(db, report_id):
    """Get report in markdown format."""
    report = await db.medical_reports.find_one({"report_id": report_id})

    if not report:
        print(f"Report not found: {report_id}")
        return

    if report.get('markdown_content'):
        print("\n" + "="*60)
        print("MARKDOWN REPORT")
        print("="*60 + "\n")
        print(report['markdown_content'])
    else:
        print("No markdown content available for this report.")


async def export_report_json(db, report_id, output_file=None):
    """Export report to JSON file."""
    report = await db.medical_reports.find_one({"report_id": report_id})

    if not report:
        print(f"Report not found: {report_id}")
        return

    # Remove MongoDB _id for cleaner JSON
    report.pop('_id', None)

    # Convert datetime to string
    if 'created_at' in report:
        report['created_at'] = report['created_at'].isoformat()

    output_file = output_file or f"report_{report_id}.json"

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Report exported to: {output_file}")


async def get_stats(db):
    """Get database statistics."""
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)

    # Count documents
    users_count = await db.users.count_documents({})
    reports_count = await db.medical_reports.count_documents({})
    kb_count = await db.knowledge_base.count_documents({})

    print(f"\nTotal Users: {users_count}")
    print(f"Total Reports: {reports_count}")
    print(f"Knowledge Base Items: {kb_count}")

    # Recent activity
    recent_reports = await db.medical_reports.find().sort("created_at", -1).limit(1).to_list(length=1)

    if recent_reports:
        last_report = recent_reports[0]
        print(f"\nLast Report Generated:")
        print(f"  Date: {last_report['created_at']}")
        print(f"  User: {last_report['user_id']}")
        print(f"  Report ID: {last_report['report_id']}")

    # Categories statistics
    if kb_count > 0:
        categories = await db.knowledge_base.distinct("category")
        print(f"\nKnowledge Base Categories: {', '.join(categories)}")

    print("\n" + "="*60)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Check reports and users in MongoDB database'
    )

    parser.add_argument(
        '--list-users',
        action='store_true',
        help='List all users'
    )
    parser.add_argument(
        '--list-reports',
        action='store_true',
        help='List all reports'
    )
    parser.add_argument(
        '--report-id',
        help='Get specific report by ID'
    )
    parser.add_argument(
        '--user-id',
        help='Filter reports by user ID'
    )
    parser.add_argument(
        '--markdown',
        action='store_true',
        help='Show report in markdown format (use with --report-id)'
    )
    parser.add_argument(
        '--export',
        help='Export report to JSON file (use with --report-id)'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show database statistics'
    )

    args = parser.parse_args()

    # Connect to database
    try:
        client, db = await connect_db()
        print(f"Connected to MongoDB: {settings.mongodb_url}")
        print(f"Database: {settings.mongodb_db_name}")
    except Exception as e:
        print(f"✗ Error connecting to MongoDB: {e}")
        print("\nMake sure MongoDB is running:")
        print("  docker-compose up -d mongodb")
        return

    try:
        # Execute command
        if args.stats:
            await get_stats(db)
        elif args.list_users:
            await list_users(db)
        elif args.list_reports:
            await list_reports(db, args.user_id)
        elif args.report_id:
            if args.markdown:
                await get_report_markdown(db, args.report_id)
            elif args.export:
                await export_report_json(db, args.report_id, args.export)
            else:
                await get_report_by_id(db, args.report_id)
        else:
            # Default: show stats and recent reports
            await get_stats(db)
            await list_reports(db)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
