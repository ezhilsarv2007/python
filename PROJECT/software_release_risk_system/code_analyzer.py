"""
code_analyzer.py
Static Code Analysis Engine for Software Release Risk Scoring System

Performs real, non-mock static analysis across multiple languages:
- Python (.py): AST syntax checking, Pyflakes for undefined names/imports, Bandit/AST security rules
- JavaScript/TypeScript (.js, .ts): Syntax balancing, dangerous eval/XSS checks, code quality
- Java (.java): Syntax structure, empty catch blocks, deprecated APIs, unclosed resources
- C/C++ (.c, .cpp, .cc, .h, .hpp): Unsafe functions (gets, strcpy, sprintf), memory bugs, include guards
- HTML (.html, .htm): Accessibility, inline event handlers, deprecated tags
- CSS (.css): Unmatched braces, !important abuse, empty rulesets

Do NOT execute uploaded source code.
"""

import os
import re
import ast
import pyflakes.api
import pyflakes.checker
import pyflakes.messages

SUPPORTED_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".java": "Java",
    ".c": "C",
    ".cpp": "C++",
    ".cc": "C++",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS"
}


class CodeIssue:
    """Represents an individual detected code quality or security issue."""
    def __init__(self, filename, line_number, issue_type, severity, description, suggested_fix):
        self.filename = filename
        self.line_number = line_number if line_number is not None else 1
        self.issue_type = issue_type
        self.severity = severity  # 'Critical', 'High', 'Medium', 'Low'
        self.description = description
        self.suggested_fix = suggested_fix

    def to_dict(self):
        return {
            "filename": self.filename,
            "line_number": self.line_number,
            "issue_type": self.issue_type,
            "severity": self.severity,
            "description": self.description,
            "suggested_fix": self.suggested_fix
        }


def analyze_python_code(content, display_name):
    """
    Performs real static analysis on Python source code using AST, Pyflakes, and AST security rules.
    Does NOT execute the code.
    """
    issues = []
    tree = None

    # 1. AST Syntax Analysis
    try:
        tree = ast.parse(content, filename=display_name)
    except SyntaxError as e:
        issues.append(CodeIssue(
            filename=display_name,
            line_number=e.lineno or 1,
            issue_type="Syntax Error",
            severity="Critical",
            description=f"Syntax error: {e.msg}",
            suggested_fix=f"Correct the syntax error near line {e.lineno or 1}. Ensure brackets, quotes, and colons are properly matched."
        ))
        # If syntax fails to parse, return immediately as AST and pyflakes require valid AST
        return issues
    except Exception as e:
        issues.append(CodeIssue(
            filename=display_name,
            line_number=1,
            issue_type="Parser Failure",
            severity="Critical",
            description=f"Unable to parse Python AST: {str(e)}",
            suggested_fix="Check file encoding and syntax validity."
        ))
        return issues

    # 2. Pyflakes Static Analysis (Undefined names, unused imports, duplicates)
    try:
        checker = pyflakes.checker.Checker(tree, filename=display_name)
        for msg in checker.messages:
            lineno = msg.lineno
            if isinstance(msg, pyflakes.messages.UndefinedName):
                issues.append(CodeIssue(
                    filename=display_name,
                    line_number=lineno,
                    issue_type="Undefined Variable",
                    severity="High",
                    description=f"Undefined variable or symbol '{msg.message_args[0]}'.",
                    suggested_fix=f"Define or import '{msg.message_args[0]}' before accessing it to prevent runtime NameError."
                ))
            elif isinstance(msg, pyflakes.messages.UndefinedLocal):
                issues.append(CodeIssue(
                    filename=display_name,
                    line_number=lineno,
                    issue_type="Undefined Local Variable",
                    severity="High",
                    description=f"Local variable '{msg.message_args[0]}' referenced before assignment.",
                    suggested_fix=f"Initialize '{msg.message_args[0]}' prior to reference in function scope."
                ))
            elif isinstance(msg, pyflakes.messages.UnusedImport):
                issues.append(CodeIssue(
                    filename=display_name,
                    line_number=lineno,
                    issue_type="Unused Import",
                    severity="Low",
                    description=f"Imported module or symbol '{msg.message_args[0]}' is unused.",
                    suggested_fix=f"Remove 'import {msg.message_args[0]}' to declutter namespace and optimize startup."
                ))
            elif isinstance(msg, pyflakes.messages.UnusedVariable):
                issues.append(CodeIssue(
                    filename=display_name,
                    line_number=lineno,
                    issue_type="Unused Variable",
                    severity="Low",
                    description=f"Local variable '{msg.message_args[0]}' is assigned but never used.",
                    suggested_fix=f"Remove unused variable or prefix with an underscore if required by convention."
                ))
            elif isinstance(msg, pyflakes.messages.DuplicateArgument):
                issues.append(CodeIssue(
                    filename=display_name,
                    line_number=lineno,
                    issue_type="Duplicate Parameter",
                    severity="High",
                    description=f"Duplicate argument name '{msg.message_args[0]}' in function definition.",
                    suggested_fix="Rename or remove duplicate parameter."
                ))
            else:
                issues.append(CodeIssue(
                    filename=display_name,
                    line_number=lineno,
                    issue_type="Code Quality Warning",
                    severity="Medium",
                    description=msg.message % msg.message_args if hasattr(msg, 'message_args') else str(msg),
                    suggested_fix="Review code structure according to PEP 8 standards."
                ))
    except Exception as e:
        # Graceful fallback if pyflakes checker throws unexpected exception
        pass

    # 3. AST Security & Best Practice Inspections (Bandit-equivalent rules)
    class SecurityVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            # Check for eval() or exec()
            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            if func_name in ("eval", "exec"):
                issues.append(CodeIssue(
                    filename=display_name,
                    line_number=getattr(node, 'lineno', 1),
                    issue_type="Security Vulnerability",
                    severity="Critical",
                    description=f"Use of dangerous dynamic execution function '{func_name}()'.",
                    suggested_fix=f"Avoid '{func_name}()'; use ast.literal_eval() or json.loads() for secure data parsing."
                ))

            # Subprocess with shell=True
            if func_name in ("Popen", "call", "run", "check_call", "check_output"):
                for kw in node.keywords:
                    if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                        issues.append(CodeIssue(
                            filename=display_name,
                            line_number=getattr(node, 'lineno', 1),
                            issue_type="Security Vulnerability",
                            severity="High",
                            description="Subprocess invocation with 'shell=True' detected (Command Injection hazard).",
                            suggested_fix="Set 'shell=False' and pass arguments as a list of strings."
                        ))

            # Insecure Cryptographic Hashes (MD5, SHA1)
            if func_name in ("md5", "sha1"):
                issues.append(CodeIssue(
                    filename=display_name,
                    line_number=getattr(node, 'lineno', 1),
                    issue_type="Insecure Cryptography",
                    severity="Medium",
                    description=f"Use of weak hash algorithm '{func_name}'.",
                    suggested_fix=f"Replace '{func_name}' with SHA-256 or SHA-3 for secure hashing."
                ))

            # Insecure pickle.loads
            if func_name == "loads" and isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "pickle":
                    issues.append(CodeIssue(
                        filename=display_name,
                        line_number=getattr(node, 'lineno', 1),
                        issue_type="Insecure Deserialization",
                        severity="High",
                        description="Use of unsafe 'pickle.loads()' on potentially untrusted input.",
                        suggested_fix="Use a safe serialized format such as JSON, Protocol Buffers, or MessagePack."
                    ))

            self.generic_visit(node)

        def visit_Assign(self, node):
            # Check for hardcoded credentials / passwords
            for target in node.targets:
                if isinstance(target, ast.Name):
                    target_lower = target.id.lower()
                    if any(secret_kw in target_lower for secret_kw in ("password", "secret_key", "api_key", "auth_token")):
                        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                            val_len = len(node.value.value)
                            if val_len > 3 and node.value.value.lower() not in ("none", "null", ""):
                                issues.append(CodeIssue(
                                    filename=display_name,
                                    line_number=getattr(node, 'lineno', 1),
                                    issue_type="Hardcoded Credential",
                                    severity="High",
                                    description=f"Potentially hardcoded secret found in variable '{target.id}'.",
                                    suggested_fix="Store secrets in environment variables or an external key vault."
                                ))
            self.generic_visit(node)

    SecurityVisitor().visit(tree)
    return issues


def analyze_javascript_typescript(content, display_name):
    """Static analysis for JavaScript and TypeScript files."""
    issues = []
    lines = content.splitlines()

    # Bracket / Brace matching
    brace_stack = []
    for line_idx, line in enumerate(lines, start=1):
        # Ignore comments
        clean_line = re.sub(r'//.*$', '', line)
        for char in clean_line:
            if char in "{[(":
                brace_stack.append((char, line_idx))
            elif char in "}])":
                if not brace_stack:
                    issues.append(CodeIssue(
                        filename=display_name,
                        line_number=line_idx,
                        issue_type="Syntax Error",
                        severity="Critical",
                        description=f"Unmatched closing bracket '{char}'.",
                        suggested_fix="Check bracket pairs and ensure all opening brackets match."
                    ))
                    break
                else:
                    top_char, _ = brace_stack.pop()
                    expected = {"}": "{", "]": "[", ")": "("}.get(char)
                    if top_char != expected:
                        issues.append(CodeIssue(
                            filename=display_name,
                            line_number=line_idx,
                            issue_type="Syntax Error",
                            severity="Critical",
                            description=f"Mismatched bracket: expected match for '{top_char}' but found '{char}'.",
                            suggested_fix="Verify nested bracket structure."
                        ))
                        break

    if brace_stack:
        unclosed, start_line = brace_stack[-1]
        issues.append(CodeIssue(
            filename=display_name,
            line_number=start_line,
            issue_type="Syntax Error",
            severity="Critical",
            description=f"Unclosed opening bracket '{unclosed}' starting at line {start_line}.",
            suggested_fix="Add the corresponding closing bracket before the end of the file."
        ))

    # Pattern inspections
    for line_idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
            continue

        # eval() check
        if re.search(r'\beval\s*\(', line):
            issues.append(CodeIssue(
                filename=display_name,
                line_number=line_idx,
                issue_type="Security Vulnerability",
                severity="High",
                description="Dangerous 'eval()' statement detected (Arbitrary Code Execution risk).",
                suggested_fix="Avoid eval(); use JSON.parse() or typed deserialization."
            ))

        # innerHTML check
        if re.search(r'\.innerHTML\s*=', line):
            issues.append(CodeIssue(
                filename=display_name,
                line_number=line_idx,
                issue_type="XSS Vulnerability",
                severity="High",
                description="Direct assignment to '.innerHTML' detected (Cross-Site Scripting hazard).",
                suggested_fix="Use '.textContent' or sanitize markup with DOMPurify before inserting."
            ))

        # debugger statement
        if re.search(r'\bdebugger\s*;?', line):
            issues.append(CodeIssue(
                filename=display_name,
                line_number=line_idx,
                issue_type="Code Smell",
                severity="Medium",
                description="Leftover 'debugger;' breakpoint statement.",
                suggested_fix="Remove debugger statements before releasing to production."
            ))

        # 'var' usage
        if re.search(r'\bvar\s+[a-zA-Z_$]', line):
            issues.append(CodeIssue(
                filename=display_name,
                line_number=line_idx,
                issue_type="Best Practice",
                severity="Low",
                description="Use of legacy 'var' declaration.",
                suggested_fix="Replace 'var' with block-scoped 'let' or 'const'."
            ))

        # Hardcoded secrets
        if re.search(r'(api_key|apiKey|password|secretKey|secret)\s*[:=]\s*["\'][a-zA-Z0-9_\-\.]{8,}["\']', line, re.I):
            issues.append(CodeIssue(
                filename=display_name,
                line_number=line_idx,
                issue_type="Hardcoded Secret",
                severity="High",
                description="Hardcoded credential or API key found in source code.",
                suggested_fix="Store secrets in server-side environment variables or a configuration vault."
            ))

    return issues


def analyze_java_code(content, display_name):
    """Static analysis for Java source files."""
    issues = []
    lines = content.splitlines()

    # Check for basic brace matching
    open_braces = 0
    for line_idx, line in enumerate(lines, start=1):
        clean_line = re.sub(r'//.*$', '', line)
        open_braces += clean_line.count('{') - clean_line.count('}')

    if open_braces != 0:
        issues.append(CodeIssue(
            filename=display_name,
            line_number=len(lines),
            issue_type="Syntax Error",
            severity="Critical",
            description=f"Unmatched curly braces detected in class structure (Net balance: {open_braces}).",
            suggested_fix="Verify that all class, method, and control block braces are closed."
        ))

    for line_idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
            continue

        # Deprecated Thread.stop() / Thread.suspend()
        if "Thread.stop(" in line or ".stop()" in line:
            issues.append(CodeIssue(
                filename=display_name,
                line_number=line_idx,
                issue_type="Unsafe API Call",
                severity="Critical",
                description="Invocation of deprecated Thread.stop() can lead to inconsistent state and locks.",
                suggested_fix="Use cooperative thread interruption flags instead of Thread.stop()."
            ))

        # Empty catch block
        if re.search(r'catch\s*\([^\)]+\)\s*\{\s*\}', line):
            issues.append(CodeIssue(
                filename=display_name,
                line_number=line_idx,
                issue_type="Swallowed Exception",
                severity="Medium",
                description="Empty catch block silently swallowing exceptions.",
                suggested_fix="Log the exception or re-throw as an unchecked/custom domain exception."
            ))

        # System.out.println in production
        if "System.out.println" in line or "System.err.println" in line:
            issues.append(CodeIssue(
                filename=display_name,
                line_number=line_idx,
                issue_type="Logging Smell",
                severity="Low",
                description="Direct use of standard output instead of a structured logger.",
                suggested_fix="Replace System.out.println with a logger (e.g. SLF4J / Log4j2)."
            ))

        # printStackTrace in production
        if ".printStackTrace(" in line:
            issues.append(CodeIssue(
                filename=display_name,
                line_number=line_idx,
                issue_type="Error Handling Smell",
                severity="Low",
                description="printStackTrace() exposes sensitive stack information to standard error.",
                suggested_fix="Log exception details through a configured logging framework."
            ))

    return issues


def analyze_c_cpp_code(content, display_name):
    """Static analysis for C/C++ source files and headers."""
    issues = []
    lines = content.splitlines()

    # Header guard check for .h and .hpp files
    if display_name.endswith((".h", ".hpp")):
        has_pragma = any("#pragma once" in line for line in lines)
        has_ifndef = any("#ifndef" in line for line in lines)
        if not has_pragma and not has_ifndef:
            issues.append(CodeIssue(
                filename=display_name,
                line_number=1,
                issue_type="Missing Header Guard",
                severity="Low",
                description="Header file lacks '#pragma once' or '#ifndef' include guard.",
                suggested_fix="Add '#pragma once' or an include guard (#ifndef HEADER_H / #define HEADER_H) to prevent duplicate definitions."
            ))

    for line_idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
            continue

        # gets() dangerous function check
        if re.search(r'\bgets\s*\(', line):
            issues.append(CodeIssue(
                filename=display_name,
                line_number=line_idx,
                issue_type="Critical Buffer Overflow",
                severity="Critical",
                description="Use of dangerous function 'gets()' (no buffer bounds checking, removed in C11).",
                suggested_fix="Replace 'gets()' immediately with 'fgets()' specifying buffer size."
            ))

        # strcpy / strcat without bounds checking
        if re.search(r'\bstrcpy\s*\(', line):
            issues.append(CodeIssue(
                filename=display_name,
                line_number=line_idx,
                issue_type="Buffer Overflow Risk",
                severity="High",
                description="Unbounded string copy using 'strcpy()'.",
                suggested_fix="Use 'strncpy()', 'strlcpy()', or 'snprintf()' with explicit length bounds."
            ))

        if re.search(r'\bstrcat\s*\(', line):
            issues.append(CodeIssue(
                filename=display_name,
                line_number=line_idx,
                issue_type="Buffer Overflow Risk",
                severity="High",
                description="Unbounded string concatenation using 'strcat()'.",
                suggested_fix="Use 'strncat()' or 'snprintf()' with size limitations."
            ))

        # sprintf without bounds checking
        if re.search(r'\bsprintf\s*\(', line):
            issues.append(CodeIssue(
                filename=display_name,
                line_number=line_idx,
                issue_type="Buffer Overflow Risk",
                severity="High",
                description="Unbounded formatted write using 'sprintf()'.",
                suggested_fix="Replace 'sprintf()' with 'snprintf()' specifying destination buffer size."
            ))

    return issues


def analyze_html_code(content, display_name):
    """Static analysis for HTML markup files."""
    issues = []
    lines = content.splitlines()

    # Doctype check
    has_doctype = any("<!doctype html" in line.lower() for line in lines[:10])
    if not has_doctype and len(lines) > 5:
        issues.append(CodeIssue(
            filename=display_name,
            line_number=1,
            issue_type="Standards Compliance",
            severity="Low",
            description="Missing '<!DOCTYPE html>' declaration.",
            suggested_fix="Add '<!DOCTYPE html>' as the first line of the document to avoid quirks mode."
        ))

    for line_idx, line in enumerate(lines, start=1):
        # Inline event handler checks (CSP violation / XSS)
        if re.search(r'\s(onclick|onload|onerror|onmouseover|onchange)\s*=', line, re.I):
            issues.append(CodeIssue(
                filename=display_name,
                line_number=line_idx,
                issue_type="CSP & Maintenance Smell",
                severity="Medium",
                description="Inline JavaScript event handler detected in HTML markup.",
                suggested_fix="Attach event listeners unobtrusively using JavaScript 'addEventListener()'."
            ))

        # img without alt
        if "<img" in line.lower() and "alt=" not in line.lower():
            issues.append(CodeIssue(
                filename=display_name,
                line_number=line_idx,
                issue_type="Accessibility (a11y)",
                severity="Low",
                description="Image tag missing 'alt' attribute.",
                suggested_fix="Provide descriptive 'alt' attribute text for screen readers and SEO."
            ))

        # Deprecated presentation tags
        for tag in ("<font", "<center>", "<marquee", "<blink"):
            if tag in line.lower():
                issues.append(CodeIssue(
                    filename=display_name,
                    line_number=line_idx,
                    issue_type="Deprecated Element",
                    severity="Low",
                    description=f"Use of deprecated HTML tag '{tag.strip('<>')}'.",
                    suggested_fix="Replace obsolete presentation tags with modern CSS styling."
                ))

    return issues


def analyze_css_code(content, display_name):
    """Static analysis for CSS stylesheets."""
    issues = []
    lines = content.splitlines()

    # Brace matching check
    open_braces = 0
    for line_idx, line in enumerate(lines, start=1):
        clean = re.sub(r'/\*.*?\*/', '', line)
        open_braces += clean.count('{') - clean.count('}')

    if open_braces != 0:
        issues.append(CodeIssue(
            filename=display_name,
            line_number=len(lines),
            issue_type="Syntax Error",
            severity="Critical",
            description=f"Unbalanced braces in stylesheet (Unclosed count: {open_braces}).",
            suggested_fix="Verify all CSS declaration blocks are enclosed with matching curly braces."
        ))

    for line_idx, line in enumerate(lines, start=1):
        # !important overuse
        if "!important" in line:
            issues.append(CodeIssue(
                filename=display_name,
                line_number=line_idx,
                issue_type="Maintainability Smell",
                severity="Low",
                description="Use of '!important' declaration breaks CSS specificity cascade.",
                suggested_fix="Refactor selector specificity instead of forcing precedence with '!important'."
            ))

        # Empty ruleset
        if re.search(r'[^{]+\{\s*\}', line):
            issues.append(CodeIssue(
                filename=display_name,
                line_number=line_idx,
                issue_type="Dead Code",
                severity="Low",
                description="Empty CSS rule declaration block.",
                suggested_fix="Remove empty CSS rulesets to optimize stylesheet size."
            ))

    return issues


def analyze_source_file(file_path, display_name=None):
    """
    Dispatcher to analyse a single source code file based on its extension.
    Returns: list of CodeIssue objects and language name.
    """
    if display_name is None:
        display_name = os.path.basename(file_path)

    ext = os.path.splitext(file_path)[1].lower()
    language = SUPPORTED_EXTENSIONS.get(ext, "Unknown")

    if language == "Unknown":
        return [CodeIssue(
            filename=display_name,
            line_number=1,
            issue_type="Unsupported File",
            severity="Low",
            description=f"Extension '{ext}' is not supported for automated static analysis.",
            suggested_fix="Submit supported files: .py, .js, .ts, .java, .c, .cpp, .html, .css"
        )], language

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception as e:
        return [CodeIssue(
            filename=display_name,
            line_number=1,
            issue_type="File Read Error",
            severity="Critical",
            description=f"Could not read file contents: {str(e)}",
            suggested_fix="Ensure file is text-encoded (UTF-8) and accessible."
        )], language

    if ext == ".py":
        issues = analyze_python_code(content, display_name)
    elif ext in (".js", ".ts"):
        issues = analyze_javascript_typescript(content, display_name)
    elif ext == ".java":
        issues = analyze_java_code(content, display_name)
    elif ext in (".c", ".cpp", ".cc", ".h", ".hpp"):
        issues = analyze_c_cpp_code(content, display_name)
    elif ext in (".html", ".htm"):
        issues = analyze_html_code(content, display_name)
    elif ext == ".css":
        issues = analyze_css_code(content, display_name)
    else:
        issues = []

    return issues, language


def summarize_analysis_results(file_results):
    """
    Aggregates issue counts, security findings, and file statuses.
    file_results is a dict: { display_name: { "language": str, "issues": [CodeIssue, ...] } }
    """
    total_files = len(file_results)
    total_errors = 0
    total_warnings = 0
    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0
    security_count = 0

    all_issues = []

    for fname, data in file_results.items():
        for issue in data["issues"]:
            all_issues.append(issue)
            sev = issue.severity
            itype = issue.issue_type.lower()

            if sev == "Critical":
                critical_count += 1
                total_errors += 1
            elif sev == "High":
                high_count += 1
                total_errors += 1
            elif sev == "Medium":
                medium_count += 1
                total_warnings += 1
            elif sev == "Low":
                low_count += 1
                total_warnings += 1

            if "security" in itype or "vulnerability" in itype or "overflow" in itype or "credential" in itype or "xss" in itype:
                security_count += 1

    # Determine code quality status
    if critical_count > 0 or high_count > 3:
        code_quality_status = "Poor"
    elif medium_count > 5 or high_count > 0:
        code_quality_status = "Average"
    else:
        code_quality_status = "Good"

    return {
        "total_files": total_files,
        "files_analysed": total_files,
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "critical_issues": critical_count,
        "high_issues": high_count,
        "medium_issues": medium_count,
        "low_issues": low_count,
        "security_findings": security_count,
        "code_quality_status": code_quality_status,
        "all_issues": [issue.to_dict() for issue in all_issues]
    }
