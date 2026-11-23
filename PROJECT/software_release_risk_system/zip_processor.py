"""
zip_processor.py
Safe ZIP Archive Processing Module for Software Release Risk Scoring System

Handles:
1. Safe ZIP extraction with path traversal (Zip Slip) protection
2. Size and file-count bounds to prevent zip-bomb denial of service
3. Folder exclusion (node_modules, .git, __pycache__, virtual environments, etc.)
4. Discovery of supported source code files
5. Clean-up of temporary extraction directories
"""

import os
import zipfile
import tempfile
from code_analyzer import SUPPORTED_EXTENSIONS

# Safety limits
MAX_ZIP_UPLOAD_BYTES = 25 * 1024 * 1024       # 25 MB upload limit
MAX_UNCOMPRESSED_BYTES = 60 * 1024 * 1024     # 60 MB total extraction limit
MAX_FILES_COUNT = 300                         # Max supported files per ZIP

IGNORED_DIRECTORIES = {
    "node_modules", ".git", "__pycache__", ".venv", "venv", "env",
    ".idea", ".vscode", "dist", "build", ".pytest_cache", ".eggs",
    ".mypy_cache", ".tox", "vendor", "bin", "obj"
}


class ZipProcessingError(Exception):
    """Custom exception raised for invalid or insecure ZIP files."""
    pass


def is_path_safe(base_dir, path):
    """
    Prevents Zip Slip directory traversal vulnerabilities by verifying
    that the canonical target path remains strictly inside the base directory.
    """
    canonical_base = os.path.abspath(base_dir)
    canonical_target = os.path.abspath(os.path.join(base_dir, path))
    return os.path.commonpath([canonical_base, canonical_target]) == canonical_base


def process_zip_archive(zip_file_path):
    """
    Safely validates, unpacks, and discovers supported source code files from a ZIP archive.
    Returns:
        temp_dir_obj (tempfile.TemporaryDirectory): Must be closed by caller in finally block.
        discovered_files (list of tuples): [(abs_path, relative_display_name), ...]
        total_discovered (int): Total supported source files found.
    Raises:
        ZipProcessingError on corrupted, oversized, or malicious ZIP archives.
    """
    # 1. Check file size
    if os.path.getsize(zip_file_path) > MAX_ZIP_UPLOAD_BYTES:
        raise ZipProcessingError(f"ZIP file exceeds the maximum allowed upload limit of {MAX_ZIP_UPLOAD_BYTES // (1024 * 1024)} MB.")

    # 2. Check if valid zipfile
    if not zipfile.is_zipfile(zip_file_path):
        raise ZipProcessingError("Uploaded file is not a valid or readable ZIP archive.")

    temp_dir_obj = tempfile.TemporaryDirectory()
    extract_path = temp_dir_obj.name
    total_uncompressed = 0
    file_count = 0

    try:
        with zipfile.ZipFile(zip_file_path, "r") as zf:
            # Test ZIP integrity
            corrupted = zf.testzip()
            if corrupted is not None:
                raise ZipProcessingError(f"Corrupted file detected inside archive: '{corrupted}'.")

            infolist = zf.infolist()
            if not infolist:
                raise ZipProcessingError("The uploaded ZIP archive is completely empty.")

            # Validate all members before extracting any
            for member in infolist:
                # Security Check: Zip Slip Path Traversal
                if not is_path_safe(extract_path, member.filename):
                    raise ZipProcessingError(f"Security Alert: Malicious path traversal detected in ZIP entry '{member.filename}'.")

                # Accumulate size and file counts (skip directories)
                if not member.is_dir():
                    total_uncompressed += member.file_size
                    file_count += 1

                if total_uncompressed > MAX_UNCOMPRESSED_BYTES:
                    raise ZipProcessingError(f"Extraction aborted: Uncompressed size exceeds {MAX_UNCOMPRESSED_BYTES // (1024 * 1024)} MB limit.")

                if file_count > MAX_FILES_COUNT:
                    raise ZipProcessingError(f"Archive contains more than {MAX_FILES_COUNT} files. Please upload a smaller sub-module.")

            # Safe Extraction
            zf.extractall(extract_path)

        # 3. Discover supported source files while ignoring excluded directories
        discovered_files = []

        for root, dirs, files in os.walk(extract_path):
            # Prune ignored directory trees in-place
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES and not d.startswith(".")]

            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    abs_file = os.path.join(root, filename)
                    # Compute clean relative path for display in results
                    rel_name = os.path.relpath(abs_file, extract_path).replace("\\", "/")
                    discovered_files.append((abs_file, rel_name))

        if not discovered_files:
            raise ZipProcessingError(
                "No supported source code files were found in the uploaded archive. "
                "Supported formats: .py, .java, .c, .cpp, .js, .ts, .html, .css"
            )

        return temp_dir_obj, discovered_files, len(discovered_files)

    except Exception:
        # Clean up temporary directory if an error occurred during processing
        temp_dir_obj.cleanup()
        raise
