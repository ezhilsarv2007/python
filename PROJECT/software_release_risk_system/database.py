"""
database.py
SQLite Database Handler for Software Release Risk Scoring System

Handles database initialization, storing new assessment records (manual and code analysis),
and fetching historical assessment results.
"""

import sqlite3
import os
import json
from datetime import datetime

# Path to SQLite database file
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database")
DB_PATH = os.path.join(DB_DIR, "assessments.db")


def get_db_connection():
    """
    Creates and returns a connection to the SQLite database.
    Sets row_factory to sqlite3.Row for dictionary-like access.
    """
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initializes the assessments and code_analyses tables if they do not already exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table 1: Manual Parameter Risk Assessments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            version TEXT NOT NULL,
            unresolved_bugs INTEGER NOT NULL,
            critical_blockers INTEGER NOT NULL,
            modified_files INTEGER NOT NULL,
            test_completion REAL NOT NULL,
            security_issues INTEGER NOT NULL,
            performance_status TEXT NOT NULL,
            code_quality TEXT NOT NULL,
            documentation_status TEXT NOT NULL,
            risk_score REAL NOT NULL,
            risk_category TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            report_filename TEXT
        )
    """)

    # Table 2: Static Code Upload & Project Analyses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS code_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            upload_type TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            total_files INTEGER NOT NULL,
            files_analysed INTEGER NOT NULL,
            total_errors INTEGER NOT NULL,
            total_warnings INTEGER NOT NULL,
            critical_issues INTEGER NOT NULL,
            security_findings INTEGER NOT NULL,
            code_quality_status TEXT NOT NULL,
            risk_score REAL NOT NULL,
            risk_category TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            report_filename TEXT,
            analysis_json TEXT
        )
    """)

    conn.commit()
    conn.close()


# ============================================================================
# Manual Assessment Functions
# ============================================================================

def save_assessment(cleaned_data, calculation_results, report_filename=None):
    """
    Inserts a newly computed manual assessment into the SQLite database.
    Returns the integer ID of the inserted record.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO assessments (
            project_name, version, unresolved_bugs, critical_blockers,
            modified_files, test_completion, security_issues,
            performance_status, code_quality, documentation_status,
            risk_score, risk_category, timestamp, report_filename
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cleaned_data["project_name"],
        cleaned_data["version"],
        cleaned_data["unresolved_bugs"],
        cleaned_data["critical_blockers"],
        cleaned_data["modified_files"],
        cleaned_data["test_completion"],
        cleaned_data["security_issues"],
        cleaned_data["performance_status"],
        cleaned_data["code_quality"],
        cleaned_data["documentation_status"],
        calculation_results["overall_score"],
        calculation_results["risk_category"],
        timestamp_str,
        report_filename
    ))

    assessment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return assessment_id


def update_report_filename(assessment_id, report_filename):
    """Updates the report_filename for an existing manual assessment record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE assessments SET report_filename = ? WHERE id = ?", (report_filename, assessment_id))
    conn.commit()
    conn.close()


def get_all_assessments():
    """Retrieves all manual assessments ordered by most recent first."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assessments ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_assessment_by_id(assessment_id):
    """Retrieves a single manual assessment record by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assessments WHERE id = ?", (assessment_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


# ============================================================================
# Code Analysis Functions (New)
# ============================================================================

def save_code_analysis(meta_data, summary_data, risk_results, issues_list, report_filename=None):
    """
    Inserts a completed code analysis record into the code_analyses SQLite table.
    Returns the integer ID of the inserted record.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Serialize complete issues list and breakdown to JSON
    analysis_payload = json.dumps({
        "summary": summary_data,
        "risk_breakdown": risk_results.get("breakdown", []),
        "issues": issues_list,
        "recommendations": risk_results.get("recommendations", [])
    })

    cursor.execute("""
        INSERT INTO code_analyses (
            project_name, upload_type, original_filename,
            total_files, files_analysed, total_errors, total_warnings,
            critical_issues, security_findings, code_quality_status,
            risk_score, risk_category, timestamp, report_filename, analysis_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        meta_data["project_name"],
        meta_data["upload_type"],
        meta_data["original_filename"],
        summary_data["total_files"],
        summary_data["files_analysed"],
        summary_data["total_errors"],
        summary_data["total_warnings"],
        summary_data["critical_issues"],
        summary_data["security_findings"],
        summary_data["code_quality_status"],
        risk_results["overall_score"],
        risk_results["risk_category"],
        timestamp_str,
        report_filename,
        analysis_payload
    ))

    analysis_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return analysis_id


def update_code_analysis_report(analysis_id, report_filename):
    """Updates the report_filename for a code analysis record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE code_analyses SET report_filename = ? WHERE id = ?", (report_filename, analysis_id))
    conn.commit()
    conn.close()


def get_all_code_analyses():
    """Retrieves all code upload analyses ordered by most recent first."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM code_analyses ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_code_analysis_by_id(analysis_id):
    """Retrieves a single code analysis record by its ID with parsed JSON payload."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM code_analyses WHERE id = ?", (analysis_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None

    data = dict(row)
    if data.get("analysis_json"):
        try:
            data["parsed_analysis"] = json.loads(data["analysis_json"])
        except Exception:
            data["parsed_analysis"] = {}
    else:
        data["parsed_analysis"] = {}

    return data
