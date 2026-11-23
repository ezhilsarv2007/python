/**
 * script.js
 * JavaScript for Software Release Risk Scoring System
 * Handles:
 * 1. Client-side form validation for manual assessments
 * 2. Upload mode switching (ZIP Archive vs. Single Code File)
 * 3. File selection preview and file-size formatting
 * 4. File-wise analysis accordion expand/collapse
 * 5. Chart.js rendering for parameter contributions
 */

// =========================================================================
// Upload Mode Switching (ZIP vs Single File)
// =========================================================================
function switchUploadMode(mode) {
    const uploadTypeInput = document.getElementById("upload_type");
    const tabZip = document.getElementById("tabZip");
    const tabSingle = document.getElementById("tabSingle");
    const zipInfo = document.getElementById("zipInfo");
    const singleInfo = document.getElementById("singleInfo");
    const fileInput = document.getElementById("code_file");
    const uploadPromptText = document.getElementById("uploadPromptText");
    const uploadSubtext = document.getElementById("uploadSubtext");
    const statusBox = document.getElementById("fileSelectedStatus");

    if (!uploadTypeInput) return;

    // Reset file input value on switch
    if (fileInput) fileInput.value = "";
    if (statusBox) statusBox.style.display = "none";

    uploadTypeInput.value = mode;

    if (mode === "zip_project") {
        if (tabZip) tabZip.classList.add("active");
        if (tabSingle) tabSingle.classList.remove("active");
        if (zipInfo) zipInfo.style.display = "block";
        if (singleInfo) singleInfo.style.display = "none";
        if (fileInput) fileInput.setAttribute("accept", ".zip");
        if (uploadPromptText) uploadPromptText.textContent = "Click to choose a .zip project archive";
        if (uploadSubtext) uploadSubtext.textContent = "Maximum archive upload size: 25 MB";
    } else {
        if (tabSingle) tabSingle.classList.add("active");
        if (tabZip) tabZip.classList.remove("active");
        if (singleInfo) singleInfo.style.display = "block";
        if (zipInfo) zipInfo.style.display = "none";
        if (fileInput) fileInput.setAttribute("accept", ".py,.java,.c,.cpp,.cc,.h,.hpp,.js,.ts,.html,.htm,.css");
        if (uploadPromptText) uploadPromptText.textContent = "Click to choose an individual source code file";
        if (uploadSubtext) uploadSubtext.textContent = "Supports .py, .java, .c, .cpp, .js, .ts, .html, .css";
    }
}

// =========================================================================
// File Selection Handler
// =========================================================================
function handleFileSelected(input) {
    const statusBox = document.getElementById("fileSelectedStatus");
    const nameSpan = document.getElementById("selectedFileName");
    const sizeSpan = document.getElementById("selectedFileSize");

    if (!input.files || input.files.length === 0) {
        if (statusBox) statusBox.style.display = "none";
        return;
    }

    const file = input.files[0];
    let sizeStr = "";
    if (file.size > 1024 * 1024) {
        sizeStr = "(" + (file.size / (1024 * 1024)).toFixed(2) + " MB)";
    } else {
        sizeStr = "(" + (file.size / 1024).toFixed(1) + " KB)";
    }

    if (nameSpan) nameSpan.textContent = file.name;
    if (sizeSpan) sizeSpan.textContent = sizeStr;
    if (statusBox) statusBox.style.display = "flex";
}

// =========================================================================
// Accordion Expand/Collapse for File-wise Analysis
// =========================================================================
function toggleFileSection(button) {
    const body = button.nextElementSibling;
    const arrow = button.querySelector(".accordion-arrow");
    if (!body) return;

    if (body.style.display === "none" || getComputedStyle(body).display === "none") {
        body.style.display = "block";
        if (arrow) arrow.innerHTML = "&#9662;"; // Down arrow
    } else {
        body.style.display = "none";
        if (arrow) arrow.innerHTML = "&#9656;"; // Right arrow
    }
}

let allExpanded = true;
function toggleAllFiles() {
    const bodies = document.querySelectorAll(".file-accordion-body");
    const arrows = document.querySelectorAll(".accordion-arrow");
    allExpanded = !allExpanded;

    bodies.forEach(function (body) {
        body.style.display = allExpanded ? "block" : "none";
    });

    arrows.forEach(function (arrow) {
        arrow.innerHTML = allExpanded ? "&#9662;" : "&#9656;";
    });
}

// =========================================================================
// DOM Ready Event Handlers
// =========================================================================
document.addEventListener("DOMContentLoaded", function () {
    // 1. Manual Assessment Form Validation (Preserved)
    const assessmentForm = document.getElementById("assessmentForm");

    if (assessmentForm) {
        assessmentForm.addEventListener("submit", function (event) {
            let isValid = true;
            let errorMessages = [];

            const projectName = document.getElementById("project_name");
            const version = document.getElementById("version");

            if (!projectName.value.trim()) {
                isValid = false;
                errorMessages.push("Software / Project Name is required.");
            }

            if (!version.value.trim()) {
                isValid = false;
                errorMessages.push("Software Version is required.");
            }

            const integerFields = [
                { id: "unresolved_bugs", label: "Unresolved Bugs" },
                { id: "critical_blockers", label: "Critical Blockers" },
                { id: "modified_files", label: "Modified Code Files" },
                { id: "security_issues", label: "Security Issues" }
            ];

            integerFields.forEach(function (field) {
                const el = document.getElementById(field.id);
                if (el) {
                    const val = parseInt(el.value, 10);
                    if (isNaN(val)) {
                        isValid = false;
                        errorMessages.push(field.label + " must be a valid whole number.");
                    } else if (val < 0) {
                        isValid = false;
                        errorMessages.push(field.label + " cannot be negative.");
                    }
                }
            });

            const testComp = document.getElementById("test_completion");
            if (testComp) {
                const val = parseFloat(testComp.value);
                if (isNaN(val)) {
                    isValid = false;
                    errorMessages.push("Test Completion Percentage is required.");
                } else if (val < 0 || val > 100) {
                    isValid = false;
                    errorMessages.push("Test Completion Percentage must be between 0 and 100.");
                }
            }

            if (!isValid) {
                event.preventDefault();
                alert("Please correct the following errors before submitting:\n\n- " + errorMessages.join("\n- "));
            }
        });
    }

    // 2. Chart.js Visual Bar Chart (Results Page)
    const chartCanvas = document.getElementById("riskContributionChart");

    if (chartCanvas && window.riskBreakdownData) {
        if (typeof Chart !== "undefined") {
            const ctx = chartCanvas.getContext("2d");
            new Chart(ctx, {
                type: "bar",
                data: {
                    labels: window.riskBreakdownData.labels,
                    datasets: [
                        {
                            label: "Risk Point Contribution (Weighted)",
                            data: window.riskBreakdownData.contributions,
                            backgroundColor: "rgba(29, 78, 216, 0.75)",
                            borderColor: "rgb(29, 78, 216)",
                            borderWidth: 1,
                            borderRadius: 4
                        },
                        {
                            label: "Raw Parameter Sub-Score (0-100)",
                            data: window.riskBreakdownData.subScores,
                            backgroundColor: "rgba(148, 163, 184, 0.35)",
                            borderColor: "rgb(100, 116, 139)",
                            borderWidth: 1,
                            borderRadius: 4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: { display: true, text: "Points (Scale 0 - 100)" }
                        },
                        x: {
                            grid: { display: false }
                        }
                    }
                }
            });
        }
    }
});
