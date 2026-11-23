"""
app.py
Flask Application for Software Release Risk Scoring System

A Python-based web application to assess risks involved in a software release
prior to production deployment via:
1. Static Source Code & ZIP Project Upload Analysis
2. Quality Parameters & Release Metrics Risk Assessment
"""

import os
import tempfile
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort
from werkzeug.utils import secure_filename

# Import modular components
from risk_calculator import (
    validate_assessment_inputs,
    calculate_risk,
    calculate_code_analysis_risk
)
from database import (
    init_db,
    save_assessment,
    update_report_filename,
    get_all_assessments,
    get_assessment_by_id,
    save_code_analysis,
    update_code_analysis_report,
    get_all_code_analyses,
    get_code_analysis_by_id
)
from report_generator import (
    generate_text_report,
    generate_code_analysis_report,
    REPORTS_DIR
)
from code_analyzer import (
    analyze_source_file,
    summarize_analysis_results,
    SUPPORTED_EXTENSIONS
)
from zip_processor import (
    process_zip_archive,
    ZipProcessingError,
    MAX_ZIP_UPLOAD_BYTES
)

app = Flask(__name__)
app.secret_key = "student_project_secret_key_release_risk_system"
app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024  # 30 MB global request size limit

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_projects")

# Initialize SQLite database tables on startup
init_db()


# ============================================================================
# Home & Navigation Routes
# ============================================================================

@app.route("/")
def index():
    """Home page route displaying project overview, upload options, and purpose."""
    return render_template("index.html")


@app.route("/about")
def about():
    """About page presenting project overview, methodology, and static analysis tools."""
    return render_template("about.html")


# ============================================================================
# Code Upload & Analysis Routes
# ============================================================================

@app.route("/upload", methods=["GET"])
def upload_page():
    """Renders the code upload page offering ZIP Project and Single File options."""
    return render_template("upload.html", supported_extensions=SUPPORTED_EXTENSIONS)


@app.route("/download-sample/<filename>")
def download_sample(filename):
    """Serves sample ZIP project archives for evaluation testing."""
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(SAMPLES_DIR, safe_filename)
    if not os.path.isfile(filepath):
        abort(404, description="Sample file not found.")
    return send_from_directory(
        SAMPLES_DIR,
        safe_filename,
        as_attachment=True,
        download_name=safe_filename
    )


@app.route("/analyze-upload", methods=["POST"])
def analyze_upload():
    """
    Handles file upload (ZIP or Individual File), executes real static analysis,
    calculates release risk, stores audit record in SQLite, and generates report.
    """
    upload_type = request.form.get("upload_type", "single_file").strip()
    project_name = request.form.get("project_name", "").strip()
    test_comp_raw = request.form.get("test_completion", "80.0").strip()

    # Validate test completion input
    try:
        test_completion = float(test_comp_raw)
        if test_completion < 0.0 or test_completion > 100.0:
            test_completion = 80.0
    except ValueError:
        test_completion = 80.0

    if "code_file" not in request.files:
        flash("No file was selected for upload.", "error")
        return redirect(url_for("upload_page"))

    uploaded_file = request.files["code_file"]
    if not uploaded_file or uploaded_file.filename == "":
        flash("Please choose a valid file to upload.", "error")
        return redirect(url_for("upload_page"))

    original_filename = secure_filename(uploaded_file.filename)
    if not original_filename:
        flash("Invalid filename provided.", "error")
        return redirect(url_for("upload_page"))

    # Default project name if omitted
    if not project_name:
        project_name = os.path.splitext(original_filename)[0].replace("_", " ").title()

    file_ext = os.path.splitext(original_filename)[1].lower()

    # -------------------------------------------------------------
    # OPTION 1: Upload Complete Project (ZIP Archive)
    # -------------------------------------------------------------
    if upload_type == "zip_project":
        if file_ext != ".zip":
            flash("Option 1 requires a valid .zip archive file.", "error")
            return redirect(url_for("upload_page"))

        # Save uploaded zip to a temporary file
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        temp_zip_path = temp_zip.name
        temp_zip.close()

        temp_dir_obj = None
        try:
            uploaded_file.save(temp_zip_path)

            # Safely process and extract ZIP archive
            temp_dir_obj, discovered_files, total_found = process_zip_archive(temp_zip_path)

            file_results = {}
            for abs_path, rel_display_name in discovered_files:
                issues, language = analyze_source_file(abs_path, display_name=rel_display_name)
                file_results[rel_display_name] = {
                    "language": language,
                    "issues": issues
                }

            summary_data = summarize_analysis_results(file_results)

        except ZipProcessingError as e:
            flash(f"ZIP Archive Error: {str(e)}", "error")
            return redirect(url_for("upload_page"))
        except Exception as e:
            flash(f"Unexpected error while processing ZIP archive: {str(e)}", "error")
            return redirect(url_for("upload_page"))
        finally:
            if temp_dir_obj:
                temp_dir_obj.cleanup()
            if os.path.exists(temp_zip_path):
                os.remove(temp_zip_path)

    # -------------------------------------------------------------
    # OPTION 2: Upload Individual Code File
    # -------------------------------------------------------------
    else:
        if file_ext not in SUPPORTED_EXTENSIONS:
            supported_list = ", ".join(SUPPORTED_EXTENSIONS.keys())
            flash(f"Unsupported file format '{file_ext}'. Supported formats: {supported_list}", "error")
            return redirect(url_for("upload_page"))

        temp_src = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
        temp_src_path = temp_src.name
        temp_src.close()

        try:
            uploaded_file.save(temp_src_path)
            issues, language = analyze_source_file(temp_src_path, display_name=original_filename)

            file_results = {
                original_filename: {
                    "language": language,
                    "issues": issues
                }
            }
            summary_data = summarize_analysis_results(file_results)

        except Exception as e:
            flash(f"Error analysing file: {str(e)}", "error")
            return redirect(url_for("upload_page"))
        finally:
            if os.path.exists(temp_src_path):
                os.remove(temp_src_path)

    # -------------------------------------------------------------
    # Calculate Release Risk from Code Findings
    # -------------------------------------------------------------
    raw_issues_list = summary_data["all_issues"]
    user_options = {
        "test_completion": test_completion,
        "performance_status": "Good" if summary_data["critical_issues"] == 0 else "Average",
        "documentation_status": "Complete"
    }

    risk_results = calculate_code_analysis_risk(summary_data, raw_issues_list, user_options=user_options)

    # Prepare metadata for database
    meta_data = {
        "project_name": project_name,
        "upload_type": upload_type,
        "original_filename": original_filename
    }

    # Persist in SQLite
    analysis_id = save_code_analysis(meta_data, summary_data, risk_results, raw_issues_list)

    # Generate persistent .txt report file
    report_filename, _ = generate_code_analysis_report(
        project_name=project_name,
        upload_type=upload_type,
        original_filename=original_filename,
        summary_data=summary_data,
        risk_results=risk_results,
        issues_list=raw_issues_list,
        analysis_id=analysis_id
    )
    update_code_analysis_report(analysis_id, report_filename)

    flash("Static code analysis and risk assessment completed successfully!", "success")
    return redirect(url_for("analysis_result", analysis_id=analysis_id))


@app.route("/analysis-result/<int:analysis_id>")
def analysis_result(analysis_id):
    """
    Displays the analysis results dashboard for a specific code analysis record.
    """
    record = get_code_analysis_by_id(analysis_id)
    if not record:
        abort(404, description="Code analysis record not found.")

    parsed = record.get("parsed_analysis", {})
    summary = parsed.get("summary", {})
    breakdown = parsed.get("risk_breakdown", [])
    issues = parsed.get("issues", [])
    recommendations = parsed.get("recommendations", [])

    # Group issues by filename for the file-wise analysis viewer
    grouped_issues = {}
    for issue in issues:
        fn = issue.get("filename", "Unknown")
        if fn not in grouped_issues:
            grouped_issues[fn] = []
        grouped_issues[fn].append(issue)

    # Badge class for UI styling
    category = record.get("risk_category", "LOW RISK")
    if category == "LOW RISK":
        badge_class = "badge-low"
    elif category == "MEDIUM RISK":
        badge_class = "badge-medium"
    else:
        badge_class = "badge-high"

    return render_template(
        "analysis_result.html",
        analysis=record,
        summary=summary,
        breakdown=breakdown,
        issues=issues,
        grouped_issues=grouped_issues,
        recommendations=recommendations,
        badge_class=badge_class,
        report_filename=record.get("report_filename")
    )


# ============================================================================
# Manual Assessment Routes (Preserved Feature)
# ============================================================================

@app.route("/assessment", methods=["GET"])
def assessment_form():
    """Renders the manual risk assessment input form."""
    scenario = request.args.get("scenario", "").lower()
    preset = {}

    if scenario == "low":
        preset = {
            "project_name": "E-Commerce Checkout Service",
            "version": "v1.4.0",
            "unresolved_bugs": "2",
            "critical_blockers": "0",
            "modified_files": "5",
            "test_completion": "95.0",
            "security_issues": "0",
            "performance_status": "Good",
            "code_quality": "Good",
            "documentation_status": "Complete"
        }
    elif scenario == "medium":
        preset = {
            "project_name": "Customer Billing Portal",
            "version": "v2.1.0",
            "unresolved_bugs": "10",
            "critical_blockers": "0",
            "modified_files": "22",
            "test_completion": "68.0",
            "security_issues": "1",
            "performance_status": "Average",
            "code_quality": "Average",
            "documentation_status": "Complete"
        }
    elif scenario == "high":
        preset = {
            "project_name": "Core Banking Transaction Engine",
            "version": "v3.0.0-RC1",
            "unresolved_bugs": "24",
            "critical_blockers": "2",
            "modified_files": "45",
            "test_completion": "35.0",
            "security_issues": "3",
            "performance_status": "Poor",
            "code_quality": "Poor",
            "documentation_status": "Incomplete"
        }

    return render_template("assessment.html", form_data=preset, errors=[])


@app.route("/assess", methods=["POST"])
def assess():
    """Handles manual assessment form submission and redirects to result."""
    form_data = request.form.to_dict()
    is_valid, errors, cleaned = validate_assessment_inputs(form_data)

    if not is_valid:
        return render_template("assessment.html", form_data=form_data, errors=errors)

    results = calculate_risk(cleaned)
    assessment_id = save_assessment(cleaned, results)

    filename, _ = generate_text_report(cleaned, results, assessment_id=assessment_id)
    update_report_filename(assessment_id, filename)

    flash("Manual risk assessment successfully calculated and saved to history!", "success")
    return redirect(url_for("result_dashboard", assessment_id=assessment_id))


@app.route("/result/<int:assessment_id>")
def result_dashboard(assessment_id):
    """Displays results dashboard for manual parameter assessment."""
    record = get_assessment_by_id(assessment_id)
    if not record:
        abort(404, description="Assessment record not found.")

    cleaned = {
        "project_name": record["project_name"],
        "version": record["version"],
        "unresolved_bugs": record["unresolved_bugs"],
        "critical_blockers": record["critical_blockers"],
        "modified_files": record["modified_files"],
        "test_completion": record["test_completion"],
        "security_issues": record["security_issues"],
        "performance_status": record["performance_status"],
        "code_quality": record["code_quality"],
        "documentation_status": record["documentation_status"]
    }

    results = calculate_risk(cleaned)
    report_filename = record.get("report_filename")
    if not report_filename or not os.path.exists(os.path.join(REPORTS_DIR, report_filename)):
        report_filename, _ = generate_text_report(
            cleaned, results, assessment_id=assessment_id, timestamp=record["timestamp"]
        )
        update_report_filename(assessment_id, report_filename)

    return render_template(
        "result.html",
        assessment=record,
        cleaned=cleaned,
        results=results,
        report_filename=report_filename
    )


# ============================================================================
# Assessment History & Reports Routes
# ============================================================================

@app.route("/history")
def history():
    """Displays both Code Upload Analyses and Manual Assessments from SQLite."""
    code_analyses_list = get_all_code_analyses()
    assessments_list = get_all_assessments()
    return render_template(
        "history.html",
        code_analyses=code_analyses_list,
        assessments=assessments_list
    )


@app.route("/download-report/<filename>")
def download_report(filename):
    """Serves the generated .txt report file for download with directory traversal safety."""
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(REPORTS_DIR, safe_filename)
    if not os.path.isfile(filepath):
        abort(404, description="Report file does not exist.")

    return send_from_directory(
        REPORTS_DIR,
        safe_filename,
        as_attachment=True,
        download_name=safe_filename
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
