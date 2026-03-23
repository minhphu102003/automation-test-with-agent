import os
import asyncio
from datetime import datetime
from jinja2 import Template
from typing import List, Dict, Any
from playwright.async_api import async_playwright

# Premium HTML Template with Dark Mode and Glassmorphism
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Automation Test Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --text-main: #f8fafc;
            --text-dim: #94a3b8;
            --success: #10b981;
            --failure: #ef4444;
            --accent: #6366f1;
            --border: rgba(255, 255, 255, 0.1);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            line-height: 1.6;
            padding: 2rem;
            background-image: radial-gradient(circle at 50% -20%, #1e293b, #0f172a);
            min-height: 100vh;
        }

        .container { max-width: 1200px; margin: 0 auto; }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 3rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border);
        }

        h1 { font-size: 2rem; font-weight: 700; letter-spacing: -0.025em; }
        .timestamp { color: var(--text-dim); font-size: 0.875rem; }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }

        .stat-card {
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            padding: 1.5rem;
            border-radius: 1rem;
            border: 1px solid var(--border);
            text-align: center;
        }

        .stat-value { font-size: 2.5rem; font-weight: 700; margin-bottom: 0.25rem; }
        .stat-label { color: var(--text-dim); text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; }

        .stat-pass { color: var(--success); }
        .stat-fail { color: var(--failure); }

        .table-container {
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border-radius: 1rem;
            border: 1px solid var(--border);
            overflow: hidden;
        }

        table { width: 100%; border-collapse: collapse; text-align: left; }
        th {
            background: rgba(255, 255, 255, 0.05);
            padding: 1rem 1.5rem;
            font-size: 0.875rem;
            color: var(--text-dim);
            font-weight: 600;
        }

        td { padding: 1rem 1.5rem; border-top: 1px solid var(--border); vertical-align: top; }
        
        .status-badge {
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
        }

        .status-pass { background: rgba(16, 185, 129, 0.1); color: var(--success); }
        .status-fail { background: rgba(239, 68, 68, 0.1); color: var(--failure); }

        .test-id { font-family: monospace; color: var(--accent); font-weight: 600; }
        .test-title { font-weight: 500; margin-bottom: 0.25rem; display: block; }
        .test-result { font-size: 0.875rem; color: var(--text-dim); }

        tr:hover { background: rgba(255, 255, 255, 0.02); }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>Test Automation Report</h1>
                <p class="timestamp">Generated on {{ timestamp }}</p>
            </div>
            <div class="stat-label">Project: Browser Testing</div>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{{ total }}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat-card">
                <div class="stat-value stat-pass">{{ passed }}</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value stat-fail">{{ failed }}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: var(--accent);">{{ pass_rate }}%</div>
                <div class="stat-label">Pass Rate</div>
            </div>
        </div>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th style="width: 10%;">ID</th>
                        <th style="width: 25%;">Test Case Title</th>
                        <th style="width: 10%;">Status</th>
                        <th style="width: 40%;">Actual Result</th>
                        <th style="width: 15%;">Priority</th>
                    </tr>
                </thead>
                <tbody>
                    {% for tc in results %}
                    <tr>
                        <td><span class="test-id">{{ tc['Test Case ID'] or 'N/A' }}</span></td>
                        <td>
                            <span class="test-title">{{ tc['Test Case Title'] }}</span>
                            <div style="font-size: 0.75rem; color: var(--text-dim);">{{ tc['Module / Feature'] }}</div>
                        </td>
                        <td>
                            <span class="status-badge {{ 'status-pass' if tc['Status (Pass/Fail)'] == 'Pass' else 'status-fail' }}">
                                {{ tc['Status (Pass/Fail)'] }}
                            </span>
                        </td>
                        <td>
                            <div class="test-result">{{ tc['Actual Result'] }}</div>
                            {% if tc['Comments / Notes'] %}
                            <div style="margin-top: 0.5rem; font-size: 0.75rem; color: var(--accent);">
                                <strong>Note:</strong> {{ tc['Comments / Notes'] }}
                            </div>
                            {% endif %}
                        </td>
                        <td>{{ tc['Priority'] or 'Medium' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

def generate_html_report(test_results: List[Dict[str, Any]], output_path: str = "report.html"):
    """
    Generates a premium HTML report from the list of test results.
    """
    total = len(test_results)
    passed = sum(1 for tc in test_results if tc.get('Status (Pass/Fail)') == 'Pass')
    failed = total - passed
    pass_rate = round((passed / total * 100), 1) if total > 0 else 0
    
    template = Template(HTML_TEMPLATE)
    html_content = template.render(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total=total,
        passed=passed,
        failed=failed,
        pass_rate=pass_rate,
        results=test_results
    )
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✅ HTML Report generated at: {os.path.abspath(output_path)}")
    return os.path.abspath(output_path)

async def generate_pdf_report(html_path: str, pdf_path: str):
    """
    Converts the HTML report to a PDF using Playwright.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Load the local HTML file
        absolute_html_path = f"file://{os.path.abspath(html_path)}"
        await page.goto(absolute_html_path, wait_until="networkidle")
        
        # Give a small delay for any animations/rendering
        await asyncio.sleep(1)
        
        # Generate PDF
        await page.pdf(
            path=pdf_path,
            format="A4",
            print_background=True,
            margin={"top": "20px", "right": "20px", "bottom": "20px", "left": "20px"}
        )
        
        await browser.close()
    
    print(f"✅ PDF Report generated at: {os.path.abspath(pdf_path)}")
    return os.path.abspath(pdf_path)

if __name__ == "__main__":
    # Example for testing the generator locally with dummy data
    dummy_data = [
        {
            "Test Case ID": "TC-001",
            "Test Case Title": "Login Success",
            "Module / Feature": "Authen",
            "Status (Pass/Fail)": "Pass",
            "Actual Result": "Successfully logged in and saw dashboard.",
            "Priority": "High"
        },
        {
            "Test Case ID": "TC-002",
            "Test Case Title": "Login Fail",
            "Module / Feature": "Authen",
            "Status (Pass/Fail)": "Fail",
            "Actual Result": "Password error message did not appear.",
            "Priority": "Medium"
        }
    ]
    generate_html_report(dummy_data)
