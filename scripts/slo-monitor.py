#!/usr/bin/env python3
"""
FinanceHub - SLO/SLI Monitoring
Author: KAREN (DevOps Engineer)
Date: 2026-01-30
Description: Service Level Objective and Service Level Indicator tracking

This script monitors SLOs and calculates SLIs to ensure service reliability.
Based on Google SRE practices and modern observability standards.
"""

import json
import time
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import subprocess
import os

try:
    import requests
except ImportError:
    requests = None


#############################################
# SLO Configuration
#############################################


class SLOConfig:
    """Service Level Objective configuration"""

    # SLO Definitions (target percentage)
    AVAILABILITY_SLO = 99.9  # 99.9% uptime
    LATENCY_SLO_P50 = 200  # 200ms median
    LATENCY_SLO_P95 = 500  # 500ms p95
    LATENCY_SLO_P99 = 1000  # 1000ms p99
    ERROR_RATE_SLO = 0.5  # 0.5% error rate

    # Time windows for SLO calculation
    ROLLING_24H = 24 * 3600
    ROLLING_7D = 7 * 24 * 3600
    ROLLING_30D = 30 * 24 * 3600

    # Alert thresholds
    ERROR_BUDGET_THRESHOLD = 2.0  # Alert when error budget drops below 2%


class SLIMetrics:
    """Service Level Indicators"""

    @staticmethod
    def check_availability(url: str, timeout: int = 5) -> Dict[str, any]:
        """Check service availability"""
        try:
            start = time.time()
            response = requests.get(url, timeout=timeout)
            latency_ms = (time.time() - start) * 1000

            return {
                "available": response.status_code == 200,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    @staticmethod
    def check_database() -> Dict[str, any]:
        """Check database availability"""
        try:
            result = subprocess.run(
                ["psql", os.environ.get("DATABASE_URL", ""), "-c", "SELECT 1;"],
                capture_output=True,
                timeout=5,
            )
            return {
                "available": result.returncode == 0,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    @staticmethod
    def check_redis() -> Dict[str, any]:
        """Check Redis availability"""
        try:
            result = subprocess.run(
                ["redis-cli", "ping"], capture_output=True, timeout=5
            )
            return {
                "available": b"PONG" in result.stdout,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }


class SLOTracker:
    """Track and calculate SLO compliance"""

    def __init__(self, config_file: str = "./config/slo.json"):
        self.config_file = config_file
        self.metrics_history: List[Dict] = []
        self.load_history()

    def load_history(self):
        """Load historical metrics"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    self.metrics_history = data.get("metrics", [])
        except Exception:
            self.metrics_history = []

    def save_history(self):
        """Save metrics history"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(
                    {
                        "metrics": self.metrics_history,
                        "last_updated": datetime.now().isoformat(),
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            print(f"Warning: Could not save metrics: {e}")

    def record_metric(self, metric: Dict):
        """Record a new metric"""
        self.metrics_history.append(metric)
        self.save_history()

    def calculate_availability_sli(
        self, time_window: int = SLOConfig.ROLLING_24H
    ) -> Dict:
        """Calculate availability SLI over time window"""
        cutoff = datetime.now() - timedelta(seconds=time_window)
        recent_metrics = [
            m
            for m in self.metrics_history
            if datetime.fromisoformat(m["timestamp"]) > cutoff
        ]

        if not recent_metrics:
            return {"sli": 0, "samples": 0}

        available_count = sum(1 for m in recent_metrics if m.get("available", False))
        total_count = len(recent_metrics)
        sli = (available_count / total_count * 100) if total_count > 0 else 0

        return {
            "sli": round(sli, 2),
            "samples": total_count,
            "time_window_hours": time_window / 3600,
        }

    def calculate_latency_sli(self, percentile: str = "p95") -> Dict:
        """Calculate latency SLI"""
        latencies = [
            m.get("latency_ms", 0) for m in self.metrics_history if m.get("latency_ms")
        ]

        if not latencies:
            return {"sli": 0, "samples": 0}

        latencies.sort()

        # Calculate percentile
        percentile_map = {"p50": 0.5, "p95": 0.95, "p99": 0.99}
        idx = int(len(latencies) * percentile_map.get(percentile, 0.95))
        sli = latencies[idx]

        return {
            "sli": round(sli, 2),
            "samples": len(latencies),
            "percentile": percentile,
        }

    def calculate_error_budget(
        self, slo_target: float = SLOConfig.AVAILABILITY_SLO
    ) -> Dict:
        """Calculate remaining error budget"""
        availability = self.calculate_availability_sli()
        sli = availability["sli"]

        # Error budget = 100% - (SLO achieved / SLO target * 100%)
        error_budget = 100 - (sli / slo_target * 100)

        return {
            "error_budget_remaining": max(0, round(error_budget, 2)),
            "sli": sli,
            "slo_target": slo_target,
            "status": "OK" if error_budget > 0 else "BREACHED",
        }

    def check_slo_compliance(self) -> Dict:
        """Check all SLOs and return compliance status"""
        availability_sli = self.calculate_availability_sli()
        latency_sli = self.calculate_latency_sli("p95")
        error_budget = self.calculate_error_budget()

        # Check each SLO
        availability_ok = availability_sli["sli"] >= SLOConfig.AVAILABILITY_SLO
        latency_ok = latency_sli["sli"] <= SLOConfig.LATENCY_SLO_P95
        error_budget_ok = error_budget["error_budget_remaining"] > 0

        overall_ok = availability_ok and latency_ok and error_budget_ok

        return {
            "overall_status": "PASS" if overall_ok else "FAIL",
            "timestamp": datetime.now().isoformat(),
            "availability": {
                "sli": availability_sli["sli"],
                "slo": SLOConfig.AVAILABILITY_SLO,
                "status": "OK" if availability_ok else "BREACHED",
            },
            "latency_p95": {
                "sli": latency_sli["sli"],
                "slo": SLOConfig.LATENCY_SLO_P95,
                "status": "OK" if latency_ok else "BREACHED",
            },
            "error_budget": {
                "remaining": error_budget["error_budget_remaining"],
                "threshold": SLOConfig.ERROR_BUDGET_THRESHOLD,
                "status": "OK" if error_budget_ok else "CRITICAL",
            },
        }


def monitor_slos_continuously(interval: int = 60, duration: int = 3600):
    """Monitor SLOs continuously"""
    tracker = SLOTracker()
    sli = SLIMetrics()
    api_url = os.environ.get("API_URL", "http://localhost:8000/api/v1/health/")

    print(f"🚀 Starting SLO monitoring (interval: {interval}s, duration: {duration}s)")
    print("=" * 60)

    start_time = time.time()
    check_count = 0

    while time.time() - start_time < duration:
        # Collect metrics
        api_metric = sli.check_availability(api_url)
        db_metric = sli.check_database()
        redis_metric = sli.check_redis()

        # Record API metric for SLO calculation
        tracker.record_metric(api_metric)

        # Check compliance
        compliance = tracker.check_slo_compliance()
        check_count += 1

        # Print status
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_icon = "✅" if compliance["overall_status"] == "PASS" else "❌"

        print(f"\n[{timestamp}] Check #{check_count} {status_icon}")
        print(
            f"  Availability: {compliance['availability']['sli']}% "
            f"(SLO: {compliance['availability']['slo']}%) "
            f"- {compliance['availability']['status']}"
        )

        print(
            f"  Latency p95: {compliance['latency_p95']['sli']}ms "
            f"(SLO: {compliance['latency_p95']['slo']}ms) "
            f"- {compliance['latency_p95']['status']}"
        )

        print(
            f"  Error Budget: {compliance['error_budget']['remaining']}% "
            f"- {compliance['error_budget']['status']}"
        )

        print(
            f"  DB: {'✅' if db_metric['available'] else '❌'}, "
            f"Redis: {'✅' if redis_metric['available'] else '❌'}"
        )

        # Alert if SLO breached
        if compliance["overall_status"] == "FAIL":
            print("\n🚨 SLO BREACHED! Check logs for details.")
            # Here you would trigger alerts (PagerDuty, Slack, etc.)

        time.sleep(interval)

    print("\n" + "=" * 60)
    print(f"✅ Monitoring complete. Performed {check_count} checks.")


def generate_slo_report():
    """Generate comprehensive SLO report"""
    tracker = SLOTracker()

    print("\n" + "=" * 60)
    print("📊 SERVICE LEVEL OBJECTIVE REPORT")
    print("=" * 60)

    compliance = tracker.check_slo_compliance()

    print(f"\nTimestamp: {compliance['timestamp']}")
    print(f"Overall Status: {compliance['overall_status']}")

    print("\n📈 Availability:")
    print(f"  SLI: {compliance['availability']['sli']}%")
    print(f"  SLO: {compliance['availability']['slo']}%")
    print(f"  Status: {compliance['availability']['status']}")

    print("\n⏱️  Latency:")
    print(
        f"  p50: {tracker.calculate_latency_sli('p50')['sli']}ms (SLO: {SLOConfig.LATENCY_SLO_P50}ms)"
    )
    print(
        f"  p95: {tracker.calculate_latency_sli('p95')['sli']}ms (SLO: {SLOConfig.LATENCY_SLO_P95}ms)"
    )
    print(
        f"  p99: {tracker.calculate_latency_sli('p99')['sli']}ms (SLO: {SLOConfig.LATENCY_SLO_P99}ms)"
    )

    print("\n💰 Error Budget:")
    print(f"  Remaining: {compliance['error_budget']['remaining']}%")
    print(f"  Status: {compliance['error_budget']['status']}")

    print("\n" + "=" * 60)

    if compliance["overall_status"] == "FAIL":
        print("⚠️  ACTION REQUIRED: SLOs are not being met!")
    else:
        print("✅ All SLOs are being met")


def main():
    parser = argparse.ArgumentParser(description="FinanceHub SLO/SLI Monitoring")
    parser.add_argument(
        "command",
        nargs="?",
        default="report",
        choices=["monitor", "report", "check"],
        help="Command to run",
    )
    parser.add_argument(
        "--interval", type=int, default=60, help="Monitoring interval in seconds"
    )
    parser.add_argument(
        "--duration", type=int, default=3600, help="Monitoring duration in seconds"
    )

    args = parser.parse_args()

    if args.command == "monitor":
        monitor_slos_continuously(args.interval, args.duration)
    elif args.command == "report":
        generate_slo_report()
    elif args.command == "check":
        tracker = SLOTracker()
        compliance = tracker.check_slo_compliance()
        print(json.dumps(compliance, indent=2))


if __name__ == "__main__":
    main()
