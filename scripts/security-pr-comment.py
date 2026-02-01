#!/usr/bin/env python3
"""
Security PR Comment Script

This script generates and posts security scan summaries as PR comments.
It can be used standalone or integrated into CI workflows.
"""

import json
import os
import sys
from pathlib import Path


def parse_pip_audit_results(results_path: str) -> dict:
    """Parse pip-audit results JSON file."""
    try:
        with open(results_path, "r") as f:
            data = json.load(f)

        vulnerabilities = data.get("vulnerabilities", [])
        return {
            "found": len(vulnerabilities) > 0,
            "count": len(vulnerabilities),
            "details": vulnerabilities[:5],  # Top 5
        }
    except Exception as e:
        return {"found": False, "error": str(e)}


def parse_npm_audit_results(results_path: str) -> dict:
    """Parse npm audit results JSON file."""
    try:
        with open(results_path, "r") as f:
            data = json.load(f)

        metadata = data.get("metadata", {})
        vulnerabilities = metadata.get("vulnerabilities", {})

        return {
            "found": vulnerabilities.get("total", 0) > 0,
            "critical": vulnerabilities.get("critical", 0),
            "high": vulnerabilities.get("high", 0),
            "moderate": vulnerabilities.get("moderate", 0),
            "low": vulnerabilities.get("low", 0),
            "total": vulnerabilities.get("total", 0),
        }
    except Exception as e:
        return {"found": False, "error": str(e)}


def parse_trivy_results(results_path: str) -> dict:
    """Parse Trivy SARIF results file."""
    try:
        with open(results_path, "r") as f:
            data = json.load(f)

        runs = data.get("runs", [])
        if not runs:
            return {"found": False, "error": "No runs in SARIF"}

        results = runs[0].get("results", [])

        severity_count = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}

        for result in results:
            for rule in result.get("ruleId", []):
                level = result.get("level", "UNKNOWN").upper()
                if level in severity_count:
                    severity_count[level] += 1

        return {
            "found": sum(severity_count.values()) > 0,
            "severity": severity_count,
            "total": sum(severity_count.values()),
        }
    except Exception as e:
        return {"found": False, "error": str(e)}


def generate_comment_body(
    pip_results: dict,
    npm_results: dict,
    trivy_backend: dict,
    trivy_frontend: dict,
    repo_full_name: str,
) -> str:
    """Generate the PR comment body."""
    body = "## 🔒 Security Scan Results\n\n"

    # Docker Image Scanning
    body += "### 🐳 Docker Image Scanning\n\n"

    body += "**Backend:**\n"
    if "error" in trivy_backend:
        body += f"❌ Scan failed: {trivy_backend['error']}\n\n"
    elif trivy_backend["found"]:
        sev = trivy_backend["severity"]
        body += f"- CRITICAL: {sev['CRITICAL']}\n"
        body += f"- HIGH: {sev['HIGH']}\n"
        body += f"- MEDIUM: {sev['MEDIUM']}\n"
        body += f"- LOW: {sev['LOW']}\n"
        if sev["CRITICAL"] > 0 or sev["HIGH"] > 0:
            body += "⚠️ Action required\n\n"
        else:
            body += "✅ No critical issues\n\n"
    else:
        body += "✅ No vulnerabilities found\n\n"

    body += "**Frontend:**\n"
    if "error" in trivy_frontend:
        body += f"❌ Scan failed: {trivy_frontend['error']}\n\n"
    elif trivy_frontend["found"]:
        sev = trivy_frontend["severity"]
        body += f"- CRITICAL: {sev['CRITICAL']}\n"
        body += f"- HIGH: {sev['HIGH']}\n"
        body += f"- MEDIUM: {sev['MEDIUM']}\n"
        body += f"- LOW: {sev['LOW']}\n"
        if sev["CRITICAL"] > 0 or sev["HIGH"] > 0:
            body += "⚠️ Action required\n\n"
        else:
            body += "✅ No critical issues\n\n"
    else:
        body += "✅ No vulnerabilities found\n\n"

    # Dependency Scanning
    body += "### 📦 Dependency Scanning\n\n"

    body += "**Python (pip-audit):**\n"
    if "error" in pip_results:
        body += f"❌ Scan failed: {pip_results['error']}\n\n"
    elif pip_results["found"]:
        body += f"⚠️ Found {pip_results['count']} known vulnerabilities\n"
        if pip_results["details"]:
            body += "\nTop issues:\n"
            for vuln in pip_results["details"][:3]:
                name = vuln.get("name", "Unknown")
                body += f"- {name}\n"
        body += "\n"
    else:
        body += "✅ No known vulnerabilities\n\n"

    body += "**Node.js (npm audit):**\n"
    if "error" in npm_results:
        body += f"❌ Scan failed: {npm_results['error']}\n\n"
    elif npm_results["found"]:
        body += f"- Critical: {npm_results['critical']}\n"
        body += f"- High: {npm_results['high']}\n"
        body += f"- Moderate: {npm_results['moderate']}\n"
        body += f"- Low: {npm_results['low']}\n"
        if npm_results["critical"] > 0 or npm_results["high"] > 0:
            body += "\n⚠️ Action required\n\n"
        else:
            body += "\n"
    else:
        body += "✅ No known vulnerabilities\n\n"

    # Overall Status
    body += "### 📊 Overall Status\n\n"

    has_critical = (
        trivy_backend.get("severity", {}).get("CRITICAL", 0) > 0
        or trivy_frontend.get("severity", {}).get("CRITICAL", 0) > 0
        or npm_results.get("critical", 0) > 0
    )

    has_high = (
        trivy_backend.get("severity", {}).get("HIGH", 0) > 0
        or trivy_frontend.get("severity", {}).get("HIGH", 0) > 0
        or npm_results.get("high", 0) > 0
    )

    if has_critical:
        body += (
            "🚨 **CRITICAL vulnerabilities detected - Immediate action required**\n\n"
        )
    elif has_high:
        body += "⚠️ **HIGH severity vulnerabilities detected - Review recommended**\n\n"
    else:
        body += "✅ **No critical or high severity vulnerabilities found**\n\n"

    body += f"[🔗 View full details in Security tab](https://github.com/{repo_full_name}/security)\n"

    return body


def main():
    """Main entry point for the script."""
    repo_full_name = os.getenv("GITHUB_REPOSITORY", "anomalyco/FinanceHub")

    results_dir = Path(".")

    pip_results = parse_pip_audit_results(str(results_dir / "pip-audit-results.json"))
    npm_results = parse_npm_audit_results(str(results_dir / "npm-audit-results.json"))
    trivy_backend = parse_trivy_results(
        str(results_dir / "trivy-backend-results.sarif")
    )
    trivy_frontend = parse_trivy_results(
        str(results_dir / "trivy-frontend-results.sarif")
    )

    comment_body = generate_comment_body(
        pip_results, npm_results, trivy_backend, trivy_frontend, repo_full_name
    )

    print(comment_body)

    # Optionally save to file
    output_file = os.getenv("OUTPUT_FILE", "security-pr-comment.md")
    with open(output_file, "w") as f:
        f.write(comment_body)

    print(f"\nComment saved to {output_file}", file=sys.stderr)


if __name__ == "__main__":
    main()
