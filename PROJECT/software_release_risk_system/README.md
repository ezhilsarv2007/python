# Software Release Risk Scoring System
### *A Python-Based Approach for Assessing Software Release Risks with Static Code Analysis*

A clean, practical, student-developed software engineering web application built using **Python, Flask, SQLite, HTML5, CSS3, and JavaScript**. 

This system provides a dual-pathway approach to pre-deployment risk evaluation:
1. **Automated Static Code Analysis:** Upload entire software repositories as **ZIP archives** (Option 1) or **individual source files** (Option 2) across 8 programming languages without executing arbitrary code.
2. **Quality Parameter Risk Assessment:** Evaluate high-level defect density, test verification rates, and operational readiness via a weighted mathematical scoring model.

---

## 1. Key Features & Upload Options

### Option 1: Upload Complete Project (ZIP Archive)
- Safely extracts `.zip` archives into isolated temporary directories.
- Built-in **Zip Slip path traversal prevention** and extraction size limits (25 MB upload / 60 MB uncompressed / 300 files maximum).
- Automatically skips build artifacts and virtual environments: `node_modules`, `.git`, `__pycache__`, `.venv`, `venv`, `dist`, `build`.
- Scans and audits all discovered source files, aggregate issues, and computes composite release risk.
- Cleans up temporary directories immediately after analysis.

### Option 2: Upload Individual Source Code File
- Direct inspection of individual code files without archive overhead.
- Supports 8 major development languages:
  - **Python (`.py`):** Syntax check via standard library `ast`, undefined variables & unused imports via `pyflakes`, and security checks via AST/Bandit rules (`eval`, `exec`, `shell=True`, hardcoded secrets, weak cryptography).
  - **JavaScript & TypeScript (`.js`, `.ts`):** Bracket balancing, dangerous `eval()`, XSS checks (`innerHTML`), leftover `debugger;` breakpoints, and `var` usage.
  - **Java (`.java`):** Class/method brace integrity, swallowed empty `catch` blocks, deprecated `Thread.stop()`, and unclosed I/O streams.
  - **C / C++ (`.c`, `.cpp`, `.cc`, `.h`, `.hpp`):** Obsolete C11 `gets()` buffer overflows, unbounded `strcpy()`/`sprintf()`, and missing `#ifndef` include guards.
  - **HTML (`.html`, `.htm`):** Inline event handlers (`onclick` CSP hazards), deprecated tags (`<font>`, `<center>`), and missing image `alt` text.
  - **CSS (`.css`):** Declaration block balance, `!important` specificity overuse, and empty dead-code rulesets.

---

## 2. Risk Scoring Integration

Both pathways map their findings into the deterministic **0 to 100** weighted risk scoring model:

$$\text{Overall Release Risk Score} = \sum_{i=1}^{8} \left( \text{SubScore}_i \times \text{Weight}_i \right)$$

$$\sum \text{Weights} = 0.20 + 0.20 + 0.15 + 0.15 + 0.10 + 0.08 + 0.07 + 0.05 = 1.00 \ (100\%)$$

| Parameter | Assigned Weight | Static Code Analysis Mapping |
|---|---|---|
| **Critical Blockers** | **20% (0.20)** | Syntax errors, fatal parser failures, dangerous `gets()` calls |
| **Security Issues** | **20% (0.20)** | Detected security vulnerabilities (eval, XSS, shell=True, secrets) |
| **Test Completion** | **15% (0.15)** | Test suite completion rate ($\max(0, 100 - \text{Completion } \%)$) |
| **Unresolved Bugs** | **15% (0.15)** | High & medium defect volume (excluding security to prevent double-counting) |
| **Modified Files** | **10% (0.10)** | Number of analysed files in project ($\min(\text{Files} \times 2.5, 100)$) |
| **Performance Status** | **8% (0.08)** | Inferred performance status (Good / Average / Poor) |
| **Code Quality** | **7% (0.07)** | Overall code quality rating based on issue density |
| **Documentation Status** | **5% (0.05)** | Readiness of deployment runbooks and release notes |

### Risk Classification Thresholds:
- **`0 – 30` pts: LOW RISK** (Green) — Safe to deploy after standard automated checks.
- **`31 – 60` pts: MEDIUM RISK** (Amber) — Conditional approval; requires defect fixes & QA sign-off.
- **`61 – 100` pts: HIGH RISK** (Red) — Release blocked; immediate deployment must be halted until critical blockers are fixed.

---

## 3. Project Directory Structure

```text
software_release_risk_system/
│
├── app.py                  # Main Flask web application (routes & upload controllers)
├── code_analyzer.py        # Static analysis engine (AST, Pyflakes, Bandit-rules, C/Java/JS)
├── zip_processor.py        # Safe ZIP processing (Zip-Slip defense, size limits, cleanup)
├── risk_calculator.py      # Predefined weighted scoring & dynamic recommendation engine
├── report_generator.py     # Python file handling for downloadable .txt reports
├── database.py             # SQLite database handler (assessments & code_analyses tables)
├── run_app.bat             # Windows one-click start script
├── requirements.txt        # Python package dependencies
├── test_system.py          # Comprehensive 10-scenario test suite
├── README.md               # Project documentation
│
├── templates/              # HTML5 Jinja2 templates
│   ├── base.html           # Main layout (navbar, alerts, footer)
│   ├── index.html          # Homepage with dual assessment pathways
│   ├── upload.html         # Code upload page (ZIP project & Single file options)
│   ├── analysis_result.html# Interactive code inspection & risk dashboard
│   ├── assessment.html     # Manual quality parameters form with quick presets
│   ├── result.html         # Manual assessment results dashboard
│   ├── history.html        # Dual audit logs (Code Analyses & Manual Assessments)
│   └── about.html          # System architecture & mathematical scoring documentation
│
├── static/
│   ├── css/
│   │   └── style.css       # Clean student dashboard stylesheet
│   └── js/
│       └── script.js       # Client validation, file picker preview & Chart.js
│
├── reports/                # Downloadable generated .txt audit reports
│
└── database/
    └── assessments.db      # SQLite database storing analysis history
```

---

## 4. How to Run the Application

### Method 1: Using the Batch Script (Recommended for Windows)
Simply double-click [`run_app.bat`](file:///C:/Users/EZHIL/.gemini/antigravity/scratch/software_release_risk_system/run_app.bat) in File Explorer, or run in PowerShell:
```powershell
cd "C:\Users\EZHIL\.gemini\antigravity\scratch\software_release_risk_system"
.\run_app.bat
```

### Method 2: Using the Virtual Environment Python
```powershell
cd "C:\Users\EZHIL\.gemini\antigravity\scratch\software_release_risk_system"
& ".\.venv\Scripts\python.exe" app.py
```

### Method 3: Using Python Launcher (`py`)
```powershell
py -m pip install -r requirements.txt
py app.py
```

Once started, open your web browser at:
**`http://127.0.0.1:5000/`**

---

## 5. Automated Test Suite Verification

Run the comprehensive test suite verifying all 8 upload scenarios and preserved features:
```powershell
& ".\.venv\Scripts\python.exe" test_system.py
```

### Verified Test Results:
1. **Python with Syntax Errors:** Critical AST error flagged, line number identified, classified as `HIGH RISK`.
2. **Python with Undefined Variables:** `pyflakes` catches `unknown_tax_rate` with actionable fix suggestion.
3. **Clean Python File:** 0 errors, 0 warnings, verified as `LOW RISK`.
4. **ZIP with Multiple Python Files:** Safely unpacked, nested modules inspected, dangerous `eval()` flagged in `auth.py`.
5. **Polyglot ZIP Archive:** 5 distinct languages (.py, .js, .c, .html, .css) parsed; C `gets()` buffer overflow and JS `innerHTML` XSS caught.
6. **Corrupted ZIP:** Rejected safely with user-friendly error alert.
7. **Empty Upload:** Form validation catches empty file submission.
8. **Oversized Upload:** Size guards prevent server denial of service.
9. **Preserved Manual Assessment:** 8-parameter manual assessment form continues to calculate risk scores accurately.
10. **Report Downloads:** Downloadable `.txt` audit reports generated and served cleanly.
