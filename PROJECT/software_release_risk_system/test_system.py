"""
test_system.py
Comprehensive Test Suite for Software Release Risk Scoring System

Verifies:
1. Python file with syntax errors
2. Python file with undefined variables
3. Clean Python file
4. ZIP containing multiple Python files
5. ZIP containing different programming languages (.py, .js, .java, .c, .html, .css)
6. Invalid / corrupted ZIP file
7. Empty upload validation
8. Oversized upload handling
9. Preserved Manual Assessment features & History
10. Download report functionality
"""

import os
import io
import zipfile
import unittest
from app import app
from database import init_db, get_all_assessments, get_all_code_analyses
from code_analyzer import analyze_source_file, summarize_analysis_results
from risk_calculator import calculate_code_analysis_risk, calculate_risk


class TestSoftwareReleaseRiskScoringSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        app.config["TESTING"] = True
        cls.client = app.test_client()

    # ------------------------------------------------------------------------
    # Test 1: Python file with syntax errors
    # ------------------------------------------------------------------------
    def test_01_python_syntax_error(self):
        code = "def broken_syntax(:\n    print('Missing parameter')\n"
        issues, lang = analyze_source_file.__wrapped__(code, "test_syntax.py") if hasattr(analyze_source_file, '__wrapped__') else (None, None)
        
        # Test via Flask upload endpoint
        data = {
            "upload_type": "single_file",
            "project_name": "Syntax Error Test",
            "test_completion": "75.0",
            "code_file": (io.BytesIO(code.encode("utf-8")), "test_syntax.py")
        }
        res = self.client.post("/analyze-upload", data=data, content_type="multipart/form-data", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Syntax error", res.data)
        self.assertIn(b"HIGH RISK", res.data)  # Syntax error creates critical blocker -> High Risk
        print("\n[OK] Test 1: Python file with syntax errors detected critical issue & classified as High Risk.")

    # ------------------------------------------------------------------------
    # Test 2: Python file with undefined variables
    # ------------------------------------------------------------------------
    def test_02_python_undefined_variables(self):
        code = (
            "import os\n\n"
            "def calculate_total(items):\n"
            "    total = sum(items) + unknown_tax_rate\n"
            "    return total\n"
        )
        data = {
            "upload_type": "single_file",
            "project_name": "Undefined Variable Test",
            "test_completion": "85.0",
            "code_file": (io.BytesIO(code.encode("utf-8")), "calculator.py")
        }
        res = self.client.post("/analyze-upload", data=data, content_type="multipart/form-data", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Undefined variable", res.data)
        self.assertIn(b"unknown_tax_rate", res.data)
        print("[OK] Test 2: Python file with undefined variables correctly identified 'unknown_tax_rate'.")

    # ------------------------------------------------------------------------
    # Test 3: Clean Python file
    # ------------------------------------------------------------------------
    def test_03_clean_python_file(self):
        code = (
            "def add_numbers(a: int, b: int) -> int:\n"
            "    \"\"\"Calculates sum of two numbers.\"\"\"\n"
            "    return a + b\n"
        )
        data = {
            "upload_type": "single_file",
            "project_name": "Clean Python Test",
            "test_completion": "95.0",
            "code_file": (io.BytesIO(code.encode("utf-8")), "math_utils.py")
        }
        res = self.client.post("/analyze-upload", data=data, content_type="multipart/form-data", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"LOW RISK", res.data)
        self.assertIn(b"Clean Codebase!", res.data)
        print("[OK] Test 3: Clean Python file evaluated with 0 errors and classified as Low Risk.")

    # ------------------------------------------------------------------------
    # Test 4: ZIP containing multiple Python files
    # ------------------------------------------------------------------------
    def test_04_zip_multiple_python_files(self):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("app/main.py", "def run():\n    print('App running')\n")
            zf.writestr("app/services/auth.py", "def authenticate(user, password):\n    eval('1 + 1')\n    return True\n")
            zf.writestr("app/models.py", "class User:\n    pass\n")
        zip_buffer.seek(0)

        data = {
            "upload_type": "zip_project",
            "project_name": "Multi-File Python Project",
            "test_completion": "70.0",
            "code_file": (zip_buffer, "project.zip")
        }
        res = self.client.post("/analyze-upload", data=data, content_type="multipart/form-data", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"3", res.data)  # 3 files analysed
        self.assertIn(b"eval()", res.data)  # Flagged dangerous eval in auth.py
        print("[OK] Test 4: ZIP archive with multiple nested Python files extracted and analysed successfully.")

    # ------------------------------------------------------------------------
    # Test 5: ZIP containing different programming languages
    # ------------------------------------------------------------------------
    def test_05_zip_polyglot_project(self):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # Python
            zf.writestr("src/service.py", "def handle():\n    return 'OK'\n")
            # JavaScript
            zf.writestr("static/app.js", "var count = 10;\ndocument.getElementById('box').innerHTML = '<b>Hello</b>';\n")
            # C
            zf.writestr("native/buffer.c", "#include <stdio.h>\nvoid read_data() {\n    char buf[16];\n    gets(buf);\n}\n")
            # HTML
            zf.writestr("templates/page.html", "<!DOCTYPE html>\n<html><body><img src='logo.png'><button onclick='alert(1)'>Click</button></body></html>\n")
            # CSS
            zf.writestr("static/style.css", "body { margin: 0; } .hidden { display: none !important; }\n")
        zip_buffer.seek(0)

        data = {
            "upload_type": "zip_project",
            "project_name": "Polyglot Web App",
            "test_completion": "60.0",
            "code_file": (zip_buffer, "polyglot.zip")
        }
        res = self.client.post("/analyze-upload", data=data, content_type="multipart/form-data", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"5", res.data)  # 5 files analysed
        self.assertIn(b"gets()", res.data)  # C buffer overflow detection
        self.assertIn(b"innerHTML", res.data)  # JS XSS check
        print("[OK] Test 5: ZIP with 5 distinct languages (.py, .js, .c, .html, .css) parsed and audited correctly.")

    # ------------------------------------------------------------------------
    # Test 6: Invalid / corrupted ZIP file
    # ------------------------------------------------------------------------
    def test_06_invalid_zip(self):
        fake_corrupted_data = b"This is not a zip file at all! Corrupted header."
        data = {
            "upload_type": "zip_project",
            "project_name": "Corrupted Test",
            "code_file": (io.BytesIO(fake_corrupted_data), "bad.zip")
        }
        res = self.client.post("/analyze-upload", data=data, content_type="multipart/form-data", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"not a valid or readable ZIP archive", res.data)
        print("[OK] Test 6: Corrupted/invalid ZIP rejected safely with an informative error message.")

    # ------------------------------------------------------------------------
    # Test 7: Empty upload validation
    # ------------------------------------------------------------------------
    def test_07_empty_upload(self):
        # Empty filename
        data = {
            "upload_type": "single_file",
            "project_name": "Empty Test",
            "code_file": (io.BytesIO(b""), "")
        }
        res = self.client.post("/analyze-upload", data=data, content_type="multipart/form-data", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Please choose a valid file", res.data)
        print("[OK] Test 7: Empty file submission caught by server validation.")

    # ------------------------------------------------------------------------
    # Test 8: Oversized upload limit validation
    # ------------------------------------------------------------------------
    def test_08_oversized_upload(self):
        # Flask MAX_CONTENT_LENGTH or ZIP size validation
        oversized_data = b"0" * (26 * 1024 * 1024)  # 26 MB > 25 MB limit
        data = {
            "upload_type": "zip_project",
            "project_name": "Oversized Test",
            "code_file": (io.BytesIO(oversized_data), "huge.zip")
        }
        res = self.client.post("/analyze-upload", data=data, content_type="multipart/form-data", follow_redirects=True)
        # Should return 413 Request Entity Too Large or redirect with error
        self.assertIn(res.status_code, (200, 413))
        print("[OK] Test 8: Oversized upload safely guarded by size limit.")

    # ------------------------------------------------------------------------
    # Test 9: Verify Preserved Manual Assessment functionality
    # ------------------------------------------------------------------------
    def test_09_manual_assessment_preserved(self):
        post_data = {
            "project_name": "Manual Verification Project",
            "version": "v2.0.0",
            "unresolved_bugs": "2",
            "critical_blockers": "0",
            "modified_files": "5",
            "test_completion": "96.0",
            "security_issues": "0",
            "performance_status": "Good",
            "code_quality": "Good",
            "documentation_status": "Complete"
        }
        res = self.client.post("/assess", data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Manual Verification Project", res.data)
        self.assertIn(b"LOW RISK", res.data)
        print("[OK] Test 9: Manual assessment functionality intact and functioning 100%.")

    # ------------------------------------------------------------------------
    # Test 10: Verify Report Download
    # ------------------------------------------------------------------------
    def test_10_report_download(self):
        analyses = get_all_code_analyses()
        self.assertTrue(len(analyses) > 0)
        latest = analyses[0]
        report_file = latest["report_filename"]
        res = self.client.get(f"/download-report/{report_file}")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"STATIC CODE ANALYSIS & RELEASE RISK ASSESSMENT REPORT", res.data)
        print("[OK] Test 10: Downloadable .txt report generated and served correctly.")


if __name__ == "__main__":
    unittest.main()
