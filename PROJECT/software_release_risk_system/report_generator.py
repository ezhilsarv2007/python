"""
report_generator.py
File Handling Module for Generating Downloadable Assessment & Code Analysis Reports

Uses Python built-in file handling to create clean, formatted text reports
summarizing assessment inputs, sub-scores, overall risk classification,
identified issues, and recommended actions.
"""

import os
import re
from datetime import datetime

REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")


def sanitize_filename(name):
    """Sanitizes string for use as a valid filename across operating systems."""
    clean = re.sub(r'[\\/*?:"<>| ]', "_", name)
    return clean[:40]


def generate_text_report(cleaned_data, calculation_results, assessment_id=None, timestamp=None):
    """
    Generates a structured .txt report for manual parameter risk assessments.
    Returns: filename and full file path.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)

    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    proj_clean = sanitize_filename(cleaned_data.get("project_name", "Project"))
    ver_clean = sanitize_filename(cleaned_data.get("version", "v1.0.0"))
    id_part = f"_{assessment_id}" if assessment_id else f"_{int(datetime.now().timestamp())}"
    filename = f"ReleaseRiskReport_{proj_clean}_v{ver_clean}{id_part}.txt"
    filepath = os.path.join(REPORTS_DIR, filename)

    lines = []
    lines.append("================================================================================")
    lines.append("               SOFTWARE RELEASE RISK ASSESSMENT REPORT")
    lines.append("================================================================================")
    lines.append(f"Project Title       : {cleaned_data.get('project_name', 'N/A')}")
    lines.append(f"Software Version    : {cleaned_data.get('version', 'N/A')}")
    lines.append(f"Assessment Timestamp: {timestamp}")
    lines.append(f"Assessment ID       : {assessment_id if assessment_id else 'N/A'}")
    lines.append("--------------------------------------------------------------------------------")
    lines.append("")
    lines.append("1. EXECUTIVE SUMMARY")
    lines.append("--------------------------------------------------------------------------------")
    lines.append(f"  Overall Risk Score : {calculation_results['overall_score']} / 100")
    lines.append(f"  Risk Category      : {calculation_results['risk_category']}")
    lines.append("--------------------------------------------------------------------------------")
    lines.append("")
    lines.append("2. INPUT PARAMETERS COLLECTED")
    lines.append("--------------------------------------------------------------------------------")
    lines.append(f"  - Unresolved Bugs          : {cleaned_data.get('unresolved_bugs', 0)}")
    lines.append(f"  - Critical Blockers        : {cleaned_data.get('critical_blockers', 0)}")
    lines.append(f"  - Modified Code Files      : {cleaned_data.get('modified_files', 0)}")
    lines.append(f"  - Test Completion          : {cleaned_data.get('test_completion', 0)}%")
    lines.append(f"  - Security Issues          : {cleaned_data.get('security_issues', 0)}")
    lines.append(f"  - Performance Status       : {cleaned_data.get('performance_status', 'Good')}")
    lines.append(f"  - Code Quality             : {cleaned_data.get('code_quality', 'Good')}")
    lines.append(f"  - Documentation Status     : {cleaned_data.get('documentation_status', 'Complete')}")
    lines.append("")
    lines.append("3. INDIVIDUAL PARAMETER RISK BREAKDOWN")
    lines.append("--------------------------------------------------------------------------------")
    lines.append(f"{'Parameter':<24} | {'Raw Value':<15} | {'Sub-Score (0-100)':<18} | {'Weight':<8} | {'Contribution'}")
    lines.append("-" * 80)
    for item in calculation_results["breakdown"]:
        lines.append(
            f"{item['name']:<24} | {item['raw_value']:<15} | {item['sub_score']:<18.2f} | {item['weight']:<8} | {item['weighted_score']:.2f}"
        )
    lines.append("-" * 80)
    lines.append(f"{'TOTAL WEIGHTED RISK SCORE':<69} | {calculation_results['overall_score']:.2f} / 100")
    lines.append("")
    lines.append("4. IDENTIFIED RISK FACTORS & ISSUES")
    lines.append("--------------------------------------------------------------------------------")
    for idx, issue in enumerate(calculation_results["issues"], start=1):
        lines.append(f"  [{idx}] {issue}")
    lines.append("")
    lines.append("5. ACTIONABLE RECOMMENDATIONS")
    lines.append("--------------------------------------------------------------------------------")
    for idx, rec in enumerate(calculation_results["recommendations"], start=1):
        lines.append(f"  ({idx}) {rec}")
    lines.append("")
    lines.append("================================================================================")
    lines.append("Report generated automatically by Software Release Risk Scoring System")
    lines.append("College Project - B.Tech / BE Academic Implementation")
    lines.append("================================================================================")

    with open(filepath, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))

    return filename, filepath


def generate_code_analysis_report(project_name, upload_type, original_filename,
                                  summary_data, risk_results, issues_list,
                                  analysis_id=None, timestamp=None):
    """
    Generates a comprehensive .txt report for static code upload and ZIP analysis.
    Returns: filename and full file path.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)

    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    proj_clean = sanitize_filename(project_name)
    id_part = f"_{analysis_id}" if analysis_id else f"_{int(datetime.now().timestamp())}"
    filename = f"CodeAnalysisReport_{proj_clean}{id_part}.txt"
    filepath = os.path.join(REPORTS_DIR, filename)

    lines = []
    lines.append("================================================================================")
    lines.append("           STATIC CODE ANALYSIS & RELEASE RISK ASSESSMENT REPORT")
    lines.append("================================================================================")
    lines.append(f"Project Name        : {project_name}")
    lines.append(f"Upload Type         : {'Complete Project (ZIP Archive)' if upload_type == 'zip_project' else 'Individual Code File'}")
    lines.append(f"Source Filename     : {original_filename}")
    lines.append(f"Assessment Timestamp: {timestamp}")
    lines.append(f"Analysis ID         : #{analysis_id if analysis_id else 'N/A'}")
    lines.append("--------------------------------------------------------------------------------")
    lines.append("")
    lines.append("1. EXECUTIVE SUMMARY & RISK CLASSIFICATION")
    lines.append("--------------------------------------------------------------------------------")
    lines.append(f"  Overall Release Risk Score : {risk_results['overall_score']} / 100")
    lines.append(f"  Risk Category              : {risk_results['risk_category']}")
    lines.append(f"  Overall Code Quality       : {summary_data['code_quality_status']}")
    lines.append("--------------------------------------------------------------------------------")
    lines.append("")
    lines.append("2. ANALYSIS SUMMARY METRICS")
    lines.append("--------------------------------------------------------------------------------")
    lines.append(f"  - Total Files Uploaded     : {summary_data['total_files']}")
    lines.append(f"  - Total Files Analysed     : {summary_data['files_analysed']}")
    lines.append(f"  - Total Errors Detected    : {summary_data['total_errors']}")
    lines.append(f"  - Total Warnings           : {summary_data['total_warnings']}")
    lines.append(f"  - Critical Issues (Blockers): {summary_data['critical_issues']}")
    lines.append(f"  - Security Findings        : {summary_data['security_findings']}")
    lines.append("")
    lines.append("3. PARAMETER RISK BREAKDOWN")
    lines.append("--------------------------------------------------------------------------------")
    lines.append(f"{'Parameter':<24} | {'Raw Value':<15} | {'Sub-Score':<12} | {'Weight':<8} | {'Contribution'}")
    lines.append("-" * 80)
    for item in risk_results.get("breakdown", []):
        lines.append(
            f"{item['name']:<24} | {item['raw_value']:<15} | {item['sub_score']:<12.2f} | {item['weight']:<8} | {item['weighted_score']:.2f}"
        )
    lines.append("-" * 80)
    lines.append(f"{'TOTAL RISK SCORE':<63} | {risk_results['overall_score']:.2f} / 100")
    lines.append("")
    lines.append("4. DETECTED ISSUES & CORRECTION GUIDELINES")
    lines.append("--------------------------------------------------------------------------------")
    if not issues_list:
        lines.append("  [OK] No issues detected. All scanned source code conforms to quality standards.")
    else:
        for idx, issue in enumerate(issues_list, start=1):
            fname = issue.get("filename", "unknown")
            lineno = issue.get("line_number", 1)
            sev = issue.get("severity", "Medium")
            itype = issue.get("issue_type", "General")
            desc = issue.get("description", "")
            fix = issue.get("suggested_fix", "")

            lines.append(f"  [{idx}] {fname} (Line {lineno}) - [{sev.upper()}] {itype}")
            lines.append(f"      Description : {desc}")
            lines.append(f"      Suggested   : {fix}")
            lines.append("")
    lines.append("5. ACTIONABLE RECOMMENDATIONS")
    lines.append("--------------------------------------------------------------------------------")
    for idx, rec in enumerate(risk_results.get("recommendations", []), start=1):
        lines.append(f"  ({idx}) {rec}")
    lines.append("")
    lines.append("================================================================================")
    lines.append("Report generated automatically by Software Release Risk Scoring System")
    lines.append("Static Code Analysis & Release Quality Assessment Engine")
    lines.append("================================================================================")

    with open(filepath, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))

    return filename, filepath
