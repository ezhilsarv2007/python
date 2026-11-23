"""
generate_sample_zips.py
Generates ready-to-use sample project ZIP archives for testing the application:
1. sample_project_clean_low_risk.zip (Clean Python/JS project -> Low Risk)
2. sample_project_medium_risk.zip (Moderate warnings/code smells -> Medium Risk)
3. sample_project_high_risk.zip (Critical syntax errors, eval, gets buffer overflow -> High Risk)
"""

import os
import zipfile

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_projects")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --------------------------------------------------------------------------
# 1. Clean Project (Low Risk)
# --------------------------------------------------------------------------
zip_low_path = os.path.join(OUTPUT_DIR, "sample_project_clean_low_risk.zip")
with zipfile.ZipFile(zip_low_path, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("app/main.py", """\"\"\"
Main application entry point.
\"\"\"

def calculate_discount(price: float, discount_percent: float) -> float:
    \"\"\"Calculates discounted price cleanly.\"\"\"
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be between 0 and 100")
    return price * (1.0 - discount_percent / 100.0)

if __name__ == '__main__':
    final_price = calculate_discount(100.0, 15.0)
    print(f"Final discounted price: {final_price}")
""")
    zf.writestr("app/services/user_service.py", """\"\"\"
User management service.
\"\"\"

class UserService:
    def __init__(self):
        self.users = []

    def add_user(self, username: str) -> bool:
        if username not in self.users:
            self.users.append(username)
            return True
        return False

    def get_users_count(self) -> int:
        return len(self.users)
""")
    zf.writestr("static/js/main.js", """// Clean JavaScript client module
document.addEventListener('DOMContentLoaded', () => {
    const welcomeBox = document.getElementById('welcome-message');
    if (welcomeBox) {
        welcomeBox.textContent = 'Welcome to the clean release build!';
    }
});
""")
    zf.writestr("templates/index.html", """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>E-Commerce Portal</title>
</head>
<body>
    <h1>Welcome to our portal</h1>
    <img src="/static/logo.png" alt="Company Brand Logo">
</body>
</html>
""")

# --------------------------------------------------------------------------
# 2. Medium Risk Project (Warnings, code smells, minor defects)
# --------------------------------------------------------------------------
zip_med_path = os.path.join(OUTPUT_DIR, "sample_project_medium_risk.zip")
with zipfile.ZipFile(zip_med_path, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("src/analytics.py", """import os
import sys
import math  # Unused import

def process_metrics(data_points):
    var_unused = 100  # Unused variable
    if not data_points:
        return 0
    return sum(data_points) / len(data_points)
""")
    zf.writestr("src/web/client.js", """// Legacy var and debugger smell
var legacyUserToken = "user_session_abc";

function checkStatus() {
    debugger; // Leftover debugger statement
    console.log("Checking status...");
}
""")
    zf.writestr("src/java/DataLoader.java", """package com.example;

public class DataLoader {
    public void loadData() {
        try {
            int result = 100 / 2;
        } catch (Exception e) {
            // Empty catch block: swallowed exception
        }
    }
}
""")
    zf.writestr("templates/dashboard.html", """<!DOCTYPE html>
<html>
<body>
    <!-- Missing alt attribute on image, inline event handler -->
    <img src="banner.png">
    <button onclick="alert('Action clicked')">Click Me</button>
</body>
</html>
""")

# --------------------------------------------------------------------------
# 3. High Risk Project (Syntax errors, security vulnerabilities, buffer overflows)
# --------------------------------------------------------------------------
zip_high_path = os.path.join(OUTPUT_DIR, "sample_project_high_risk.zip")
with zipfile.ZipFile(zip_high_path, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("src/core/broken_auth.py", """# Critical syntax error & security vulnerabilities
def authenticate_user(username, password:  # Missing closing parenthesis: SyntaxError!
    eval("print('Dangerous dynamic execution')")
    return True
""")
    zf.writestr("src/core/payment.py", """# Undefined variable and hardcoded credentials
import os

def process_transaction(amount):
    api_key = "secret_live_production_token_12345"  # Hardcoded secret
    total_charged = amount + undefined_shipping_rate  # Undefined variable
    return total_charged
""")
    zf.writestr("src/native/input_handler.c", """#include <stdio.h>

void read_customer_input() {
    char user_buffer[32];
    // Critical buffer overflow vulnerability
    gets(user_buffer);
}
""")
    zf.writestr("static/admin.js", """function renderProfile(userHtml) {
    // Dangerous XSS vulnerability
    document.getElementById("profile").innerHTML = userHtml;
}
""")

print("Successfully generated sample ZIP files in:", OUTPUT_DIR)
print("1.", zip_low_path)
print("2.", zip_med_path)
print("3.", zip_high_path)
