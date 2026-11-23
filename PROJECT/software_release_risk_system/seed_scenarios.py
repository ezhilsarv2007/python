"""
seed_scenarios.py
Seeds the SQLite database with the 3 required evaluation scenarios:
Scenario 1: Low Risk
Scenario 2: Medium Risk
Scenario 3: High Risk
"""

from database import init_db, save_assessment, update_report_filename
from risk_calculator import calculate_risk
from report_generator import generate_text_report

def seed():
    init_db()

    scenarios = [
        {
            "cleaned": {
                "project_name": "E-Commerce Checkout Service",
                "version": "v1.4.0",
                "unresolved_bugs": 2,
                "critical_blockers": 0,
                "modified_files": 5,
                "test_completion": 95.0,
                "security_issues": 0,
                "performance_status": "Good",
                "code_quality": "Good",
                "documentation_status": "Complete"
            }
        },
        {
            "cleaned": {
                "project_name": "Customer Billing Portal",
                "version": "v2.1.0",
                "unresolved_bugs": 10,
                "critical_blockers": 0,
                "modified_files": 22,
                "test_completion": 68.0,
                "security_issues": 1,
                "performance_status": "Average",
                "code_quality": "Average",
                "documentation_status": "Complete"
            }
        },
        {
            "cleaned": {
                "project_name": "Core Banking Transaction Engine",
                "version": "v3.0.0-RC1",
                "unresolved_bugs": 24,
                "critical_blockers": 2,
                "modified_files": 45,
                "test_completion": 35.0,
                "security_issues": 3,
                "performance_status": "Poor",
                "code_quality": "Poor",
                "documentation_status": "Incomplete"
            }
        }
    ]

    for item in scenarios:
        cleaned = item["cleaned"]
        results = calculate_risk(cleaned)
        aid = save_assessment(cleaned, results)
        fname, _ = generate_text_report(cleaned, results, assessment_id=aid)
        update_report_filename(aid, fname)
        print(f"Seeded assessment ID #{aid}: {cleaned['project_name']} -> {results['risk_category']} ({results['overall_score']}/100)")

if __name__ == "__main__":
    seed()
