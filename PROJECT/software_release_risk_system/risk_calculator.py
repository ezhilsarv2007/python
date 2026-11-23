"""
risk_calculator.py
Core Risk Calculation Module for Software Release Risk Scoring System

Handles:
1. Manual Assessment input validation & risk calculation
2. Static Code Analysis risk calculation & dynamic recommendation generation
3. Predefined weighted scoring (0 - 100 scale)
4. Risk classification (LOW, MEDIUM, HIGH)
"""

# ============================================================================
# PARAMETER WEIGHT CONFIGURATION (Total = 1.00 / 100%)
# ============================================================================
WEIGHTS = {
    "critical_blockers": 0.20,      # 20% - Critical blockers can halt deployment
    "security_issues": 0.20,        # 20% - Security flaws pose direct vulnerability risks
    "test_completion": 0.15,        # 15% - Untested paths harbor hidden defects
    "unresolved_bugs": 0.15,        # 15% - General defect volume impairs stability
    "modified_files": 0.10,         # 10% - Code churn increases regression chances
    "performance_status": 0.08,     # 8%  - System response and throughput risks
    "code_quality": 0.07,           # 7%  - Maintainability, cyclomatic complexity
    "documentation_status": 0.05    # 5%  - Operational and handover readiness
}

# ============================================================================
# RISK CLASSIFICATION THRESHOLDS
# 0 - 30:  LOW RISK
# 31 - 60: MEDIUM RISK
# 61 - 100: HIGH RISK
# ============================================================================
THRESHOLD_LOW_MAX = 30.0
THRESHOLD_MEDIUM_MAX = 60.0


def validate_assessment_inputs(form_data):
    """
    Validates form input fields for manual risk assessment.
    Returns: (is_valid: bool, errors: list of strings, cleaned_data: dict)
    """
    errors = []
    cleaned = {}

    # 1. Project Name & Version
    project_name = form_data.get("project_name", "").strip()
    if not project_name:
        errors.append("Project Name is required.")
    cleaned["project_name"] = project_name

    version = form_data.get("version", "").strip()
    if not version:
        errors.append("Software Version is required.")
    cleaned["version"] = version

    # 2. Integer non-negative fields
    integer_fields = [
        ("unresolved_bugs", "Unresolved Bugs"),
        ("critical_blockers", "Critical Blockers"),
        ("modified_files", "Modified Code Files"),
        ("security_issues", "Security Issues")
    ]

    for field_key, field_label in integer_fields:
        val_str = form_data.get(field_key, "").strip()
        if val_str == "":
            errors.append(f"{field_label} cannot be empty.")
            cleaned[field_key] = 0
        else:
            try:
                val = int(val_str)
                if val < 0:
                    errors.append(f"{field_label} cannot be negative.")
                cleaned[field_key] = max(0, val)
            except ValueError:
                errors.append(f"{field_label} must be a valid whole number.")
                cleaned[field_key] = 0

    # 3. Test Completion Percentage (0 to 100)
    test_str = form_data.get("test_completion", "").strip()
    if test_str == "":
        errors.append("Test Completion Percentage cannot be empty.")
        cleaned["test_completion"] = 0.0
    else:
        try:
            val = float(test_str)
            if val < 0.0 or val > 100.0:
                errors.append("Test Completion Percentage must be between 0 and 100.")
            cleaned["test_completion"] = min(100.0, max(0.0, val))
        except ValueError:
            errors.append("Test Completion Percentage must be a valid number.")
            cleaned["test_completion"] = 0.0

    # 4. Categorical fields
    perf = form_data.get("performance_status", "Good").strip()
    if perf not in ["Good", "Average", "Poor"]:
        errors.append("Performance Status must be Good, Average, or Poor.")
        perf = "Good"
    cleaned["performance_status"] = perf

    cq = form_data.get("code_quality", "Good").strip()
    if cq not in ["Good", "Average", "Poor"]:
        errors.append("Code Quality must be Good, Average, or Poor.")
        cq = "Good"
    cleaned["code_quality"] = cq

    doc = form_data.get("documentation_status", "Complete").strip()
    if doc not in ["Complete", "Incomplete"]:
        errors.append("Documentation Status must be Complete or Incomplete.")
        doc = "Complete"
    cleaned["documentation_status"] = doc

    is_valid = len(errors) == 0
    return is_valid, errors, cleaned


def calculate_risk(cleaned_data):
    """
    Computes individual parameter sub-scores, weighted contributions,
    the overall risk score (0-100), risk category, issues summary, and recommendations
    for manual assessment forms.
    """
    bugs = cleaned_data["unresolved_bugs"]
    blockers = cleaned_data["critical_blockers"]
    files = cleaned_data["modified_files"]
    test_comp = cleaned_data["test_completion"]
    security = cleaned_data["security_issues"]
    perf = cleaned_data["performance_status"]
    code_q = cleaned_data["code_quality"]
    docs = cleaned_data["documentation_status"]

    # -------------------------------------------------------------
    # 1. Individual Sub-Score Calculations (0 - 100 scale)
    # -------------------------------------------------------------
    if blockers == 0:
        blockers_score = 0.0
    elif blockers == 1:
        blockers_score = 60.0
    elif blockers == 2:
        blockers_score = 85.0
    else:
        blockers_score = 100.0

    if security == 0:
        security_score = 0.0
    elif security == 1:
        security_score = 40.0
    elif security == 2:
        security_score = 70.0
    else:
        security_score = 100.0

    test_risk_score = round(max(0.0, min(100.0 - test_comp, 100.0)), 2)
    bugs_score = round(min(bugs * 6.0, 100.0), 2)
    files_score = round(min(files * 2.5, 100.0), 2)

    perf_map = {"Good": 0.0, "Average": 50.0, "Poor": 100.0}
    perf_score = perf_map.get(perf, 0.0)

    code_q_map = {"Good": 0.0, "Average": 50.0, "Poor": 100.0}
    code_q_score = code_q_map.get(code_q, 0.0)

    doc_map = {"Complete": 0.0, "Incomplete": 100.0}
    doc_score = doc_map.get(docs, 0.0)

    # -------------------------------------------------------------
    # 2. Weighted Score Calculations
    # -------------------------------------------------------------
    w_blockers = round(blockers_score * WEIGHTS["critical_blockers"], 2)
    w_security = round(security_score * WEIGHTS["security_issues"], 2)
    w_test = round(test_risk_score * WEIGHTS["test_completion"], 2)
    w_bugs = round(bugs_score * WEIGHTS["unresolved_bugs"], 2)
    w_files = round(files_score * WEIGHTS["modified_files"], 2)
    w_perf = round(perf_score * WEIGHTS["performance_status"], 2)
    w_code_q = round(code_q_score * WEIGHTS["code_quality"], 2)
    w_doc = round(doc_score * WEIGHTS["documentation_status"], 2)

    overall_score = round(
        w_blockers + w_security + w_test + w_bugs + w_files + w_perf + w_code_q + w_doc,
        2
    )
    overall_score = min(100.0, max(0.0, overall_score))

    # -------------------------------------------------------------
    # 3. Risk Classification
    # -------------------------------------------------------------
    if overall_score <= THRESHOLD_LOW_MAX:
        risk_category = "LOW RISK"
        badge_class = "badge-low"
    elif overall_score <= THRESHOLD_MEDIUM_MAX:
        risk_category = "MEDIUM RISK"
        badge_class = "badge-medium"
    else:
        risk_category = "HIGH RISK"
        badge_class = "badge-high"

    # -------------------------------------------------------------
    # 4. Summary of Identified Issues
    # -------------------------------------------------------------
    issues = []
    if blockers > 0:
        issues.append(f"{blockers} Critical Blocker(s) identified that must be resolved prior to release.")
    if security > 0:
        issues.append(f"{security} Security Issue(s) detected requiring security team audit.")
    if test_comp < 80.0:
        issues.append(f"Test completion is low ({test_comp}%), below the recommended threshold of 80%.")
    if bugs > 5:
        issues.append(f"High number of unresolved bugs ({bugs} bugs) affecting release stability.")
    if files > 20:
        issues.append(f"Significant code churn detected with {files} modified source files.")
    if perf == "Poor":
        issues.append("Performance status is marked as Poor (potential latency or throughput regression).")
    elif perf == "Average":
        issues.append("Performance is Average; load benchmarks should be verified.")
    if code_q == "Poor":
        issues.append("Code Quality is rated as Poor; high technical debt and maintainability risk.")
    elif code_q == "Average":
        issues.append("Code Quality is Average; code review sign-off recommended.")
    if docs == "Incomplete":
        issues.append("Release documentation is Incomplete, risking handover and support issues.")

    if not issues:
        issues.append("No critical issues detected. All software quality parameters are within safe thresholds.")

    # -------------------------------------------------------------
    # 5. Recommendations Based on Risk Level
    # -------------------------------------------------------------
    if risk_category == "LOW RISK":
        recommendations = [
            "Release can proceed after final verification.",
            "Maintain regular monitoring post-deployment.",
            "Keep testing and documentation updated."
        ]
    elif risk_category == "MEDIUM RISK":
        recommendations = [
            "Resolve pending bugs before pushing to production.",
            "Complete remaining testing to increase coverage above 85%.",
            "Review modified code files to prevent regression side effects.",
            "Verify security issues before deployment sign-off."
        ]
    else:
        recommendations = [
            "Avoid immediate deployment; hold current release pipeline.",
            "Resolve critical blockers immediately as top priority.",
            "Conduct additional regression and stress testing.",
            "Fix all identified security vulnerabilities.",
            "Review code quality and optimize performance bottlenecks."
        ]

    breakdown = [
        {"name": "Critical Blockers", "raw_value": f"{blockers} blockers", "sub_score": blockers_score, "weight": "20%", "weighted_score": w_blockers},
        {"name": "Security Issues", "raw_value": f"{security} issues", "sub_score": security_score, "weight": "20%", "weighted_score": w_security},
        {"name": "Test Completion", "raw_value": f"{test_comp}%", "sub_score": test_risk_score, "weight": "15%", "weighted_score": w_test},
        {"name": "Unresolved Bugs", "raw_value": f"{bugs} bugs", "sub_score": bugs_score, "weight": "15%", "weighted_score": w_bugs},
        {"name": "Modified Files", "raw_value": f"{files} files", "sub_score": files_score, "weight": "10%", "weighted_score": w_files},
        {"name": "Performance Status", "raw_value": perf, "sub_score": perf_score, "weight": "8%", "weighted_score": w_perf},
        {"name": "Code Quality", "raw_value": code_q, "sub_score": code_q_score, "weight": "7%", "weighted_score": w_code_q},
        {"name": "Documentation", "raw_value": docs, "sub_score": doc_score, "weight": "5%", "weighted_score": w_doc}
    ]

    return {
        "overall_score": overall_score,
        "risk_category": risk_category,
        "badge_class": badge_class,
        "issues": issues,
        "recommendations": recommendations,
        "breakdown": breakdown,
        "weights": WEIGHTS
    }


def calculate_code_analysis_risk(summary_data, raw_issues, user_options=None):
    """
    Connects static code analysis findings to the weighted risk scoring engine.
    Ensures no double-counting of issues across categories.
    Generates actionable dynamic recommendations based on actual findings.
    """
    if user_options is None:
        user_options = {}

    critical_count = summary_data["critical_issues"]
    security_count = summary_data["security_findings"]
    total_files = summary_data["total_files"]
    code_quality_status = summary_data["code_quality_status"]

    # Calculate defect volume avoiding double-counting with security findings
    non_security_high = 0
    non_security_med = 0
    for issue in raw_issues:
        itype = issue.get("issue_type", "").lower()
        sev = issue.get("severity", "")
        is_security = any(k in itype for k in ("security", "vulnerability", "overflow", "credential", "xss"))
        if not is_security and sev != "Critical":
            if sev == "High":
                non_security_high += 1
            elif sev == "Medium":
                non_security_med += 1

    estimated_bugs = non_security_high + (non_security_med // 2)

    test_comp = float(user_options.get("test_completion", 80.0))
    perf_status = user_options.get("performance_status", "Good" if critical_count == 0 else "Average")
    doc_status = user_options.get("documentation_status", "Complete")

    cleaned = {
        "critical_blockers": critical_count,
        "security_issues": security_count,
        "unresolved_bugs": estimated_bugs,
        "modified_files": total_files,
        "test_completion": test_comp,
        "performance_status": perf_status,
        "code_quality": code_quality_status,
        "documentation_status": doc_status
    }

    base_risk = calculate_risk(cleaned)

    # If critical issues exist (e.g. syntax errors, fatal buffer overflows),
    # the release fundamentally cannot be deployed. Ensure risk reflects HIGH RISK (>= 61.0).
    if critical_count > 0 and base_risk["overall_score"] < 65.0:
        diff = round(65.0 - base_risk["overall_score"], 2)
        base_risk["overall_score"] = 65.0
        base_risk["risk_category"] = "HIGH RISK"
        base_risk["badge_class"] = "badge-high"
        # Distribute difference into Critical Blockers contribution so breakdown total matches
        for item in base_risk["breakdown"]:
            if item["name"] == "Critical Blockers":
                item["weighted_score"] = round(item["weighted_score"] + diff, 2)
                item["sub_score"] = round(item["weighted_score"] / WEIGHTS["critical_blockers"], 2)

    # Generate targeted, dynamic recommendations grounded in actual detected issues
    dynamic_recommendations = []

    # 1. Critical Syntax & Parser Errors
    syntax_issues = [i for i in raw_issues if "syntax" in i.get("issue_type", "").lower() or i.get("severity") == "Critical"]
    if syntax_issues:
        first = syntax_issues[0]
        dynamic_recommendations.append(
            f"Fix critical syntax error in '{first['filename']}' at line {first['line_number']} before attempting build or release."
        )

    # 2. Undefined Variables & Names
    undef_issues = [i for i in raw_issues if "undefined" in i.get("issue_type", "").lower()]
    if undef_issues:
        first = undef_issues[0]
        dynamic_recommendations.append(
            f"Resolve undefined variable reference in '{first['filename']}' (line {first['line_number']}) to prevent runtime crashes."
        )

    # 3. Security Findings
    sec_issues = [i for i in raw_issues if "security" in i.get("issue_type", "").lower() or "vulnerability" in i.get("issue_type", "").lower()]
    if sec_issues:
        first = sec_issues[0]
        dynamic_recommendations.append(
            f"Remediate security issue '{first['description']}' in '{first['filename']}' (line {first['line_number']})."
        )

    # 4. Dangerous C/C++ Buffer Overflow Functions
    buffer_issues = [i for i in raw_issues if "buffer overflow" in i.get("issue_type", "").lower() or "gets" in i.get("description", "").lower()]
    if buffer_issues:
        first = buffer_issues[0]
        dynamic_recommendations.append(
            f"Replace unsafe function '{first['description']}' in '{first['filename']}' with bounded functions (fgets / snprintf)."
        )

    # 5. Code Smells & Unused Imports
    unused_issues = [i for i in raw_issues if "unused" in i.get("issue_type", "").lower()]
    if unused_issues:
        dynamic_recommendations.append(
            f"Clean up {len(unused_issues)} unused import/variable declaration(s) across analysed files to improve maintainability."
        )

    # 6. Testing Recommendation
    if test_comp < 80.0:
        dynamic_recommendations.append(
            f"Current automated test completion is {test_comp}%. Run additional unit tests to raise coverage to at least 85%."
        )

    # 7. Code Quality Status
    if code_quality_status == "Poor":
        dynamic_recommendations.append("Overall code quality is Poor; conduct peer code reviews to pay down technical debt.")

    # Fallback if code is clean
    if not dynamic_recommendations:
        dynamic_recommendations = [
            "All static code quality and security checks passed with zero errors.",
            "Release can proceed after final staging smoke tests.",
            "Maintain ongoing test suite execution and version control monitoring."
        ]

    base_risk["recommendations"] = dynamic_recommendations
    return base_risk
