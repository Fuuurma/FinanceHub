#!/usr/bin/env python3
"""
FinanceHub - Performance Testing with Locust
Author: KAREN (DevOps Engineer)
Date: 2026-01-30
Description: Load testing script for FinanceHub API

Requirements:
    pip install locust

Usage:
    locust -f locustfile.py --host=https://api.financehub.com

    Or headless mode:
    locust -f locustfile.py --headless --users 100 --spawn-rate 10 \
           --host=https://api.financehub.com --run-time 5m
"""

from locust import HttpUser, task, between, events
from locust.runners import MasterRunner
import json
import random
import time


#############################################
# Configuration
#############################################

# Test credentials (use test accounts, not production!)
TEST_USERS = [
    {"username": "test_user_1@example.com", "password": "test_password_123"},
    {"username": "test_user_2@example.com", "password": "test_password_123"},
]

# Test data
TEST_SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM"]


#############################################
# Helper Functions
#############################################


def get_random_user():
    """Get random test user credentials"""
    return random.choice(TEST_USERS)


def get_random_symbol():
    """Get random stock symbol"""
    return random.choice(TEST_SYMBOLS)


#############################################
# FinanceHub API User
#############################################


class FinanceHubUser(HttpUser):
    """
    Simulates a typical FinanceHub user behavior
    """

    # Wait time between tasks (1-3 seconds)
    wait_time = between(1, 3)

    def on_start(self):
        """
        Called when a user starts. Logs in and gets auth token.
        """
        self.client.verify = False  # Ignore SSL for testing
        self.token = None
        self.portfolio_id = None

        # Login on start
        self.login()

    def on_stop(self):
        """
        Called when a user stops. Logs out.
        """
        if self.token:
            self.logout()

    #############################################
    # Authentication Tasks
    #############################################

    @task(3)
    def login(self):
        """
        Login to get authentication token
        Weight: 3 (higher probability)
        """
        user = get_random_user()

        response = self.client.post(
            "/api/v1/auth/login/",
            json={"username": user["username"], "password": user["password"]},
            name="Login",
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access")
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})

    @task(1)
    def logout(self):
        """
        Logout (clears session)
        Weight: 1 (lower probability)
        """
        if self.token:
            self.client.post("/api/v1/auth/logout/", name="Logout")
            self.token = None
            self.client.headers.pop("Authorization", None)

    #############################################
    # Market Data Tasks
    #############################################

    @task(10)
    def get_stock_price(self):
        """
        Fetch current stock price
        Weight: 10 (very common)
        """
        if not self.token:
            return

        symbol = get_random_symbol()
        self.client.get(
            f"/api/v1/market/stocks/{symbol}/quote/", name="Get Stock Quote"
        )

    @task(5)
    def get_stock_history(self):
        """
        Fetch historical stock data
        Weight: 5 (common)
        """
        if not self.token:
            return

        symbol = get_random_symbol()
        self.client.get(
            f"/api/v1/market/stocks/{symbol}/history/",
            params={"period": "1d", "interval": "5m"},
            name="Get Stock History",
        )

    @task(3)
    def search_stocks(self):
        """
        Search for stocks
        Weight: 3
        """
        if not self.token:
            return

        queries = ["Tech", "Finance", "Apple", "Microsoft", "Google"]
        query = random.choice(queries)

        self.client.get(
            "/api/v1/market/stocks/search/", params={"q": query}, name="Search Stocks"
        )

    @task(2)
    def get_market_indices(self):
        """
        Fetch market indices (S&P 500, NASDAQ, etc.)
        Weight: 2
        """
        if not self.token:
            return

        self.client.get("/api/v1/market/indices/", name="Get Market Indices")

    #############################################
    # Portfolio Tasks
    #############################################

    @task(8)
    def get_portfolio(self):
        """
        Fetch user portfolio
        Weight: 8 (very common)
        """
        if not self.token:
            return

        response = self.client.get("/api/v1/portfolio/", name="Get Portfolio")

        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                self.portfolio_id = data[0].get("id")

    @task(4)
    def get_portfolio_performance(self):
        """
        Fetch portfolio performance metrics
        Weight: 4
        """
        if not self.token:
            return

        self.client.get(
            "/api/v1/portfolio/performance/", name="Get Portfolio Performance"
        )

    @task(3)
    def get_portfolio_holdings(self):
        """
        Fetch portfolio holdings
        Weight: 3
        """
        if not self.token or not self.portfolio_id:
            return

        self.client.get(
            f"/api/v1/portfolio/{self.portfolio_id}/holdings/",
            name="Get Portfolio Holdings",
        )

    @task(2)
    def get_portfolio_allocation(self):
        """
        Fetch portfolio allocation breakdown
        Weight: 2
        """
        if not self.token or not self.portfolio_id:
            return

        self.client.get(
            f"/api/v1/portfolio/{self.portfolio_id}/allocation/",
            name="Get Portfolio Allocation",
        )

    #############################################
    # Analytics Tasks
    #############################################

    @task(3)
    def get_watchlist(self):
        """
        Fetch user's watchlist
        Weight: 3
        """
        if not self.token:
            return

        self.client.get("/api/v1/analytics/watchlist/", name="Get Watchlist")

    @task(2)
    def get_sector_performance(self):
        """
        Fetch sector performance data
        Weight: 2
        """
        if not self.token:
            return

        self.client.get("/api/v1/analytics/sectors/", name="Get Sector Performance")

    @task(1)
    def get_risk_metrics(self):
        """
        Fetch portfolio risk metrics
        Weight: 1 (less common, resource intensive)
        """
        if not self.token or not self.portfolio_id:
            return

        self.client.get(
            f"/api/v1/analytics/portfolio/{self.portfolio_id}/risk/",
            name="Get Risk Metrics",
        )

    #############################################
    # Trading Tasks (Simulation Only)
    #############################################

    @task(1)
    def simulate_trade_preview(self):
        """
        Preview a trade (without executing)
        Weight: 1
        """
        if not self.token:
            return

        symbol = get_random_symbol()
        quantity = random.randint(1, 100)

        self.client.post(
            "/api/v1/trading/preview/",
            json={"symbol": symbol, "quantity": quantity, "side": "buy"},
            name="Preview Trade",
        )


#############################################
# Admin Tasks (Weighted very low)
#############################################


class AdminUser(FinanceHubUser):
    """
    Simulates admin user behavior (lower weight in tests)
    """

    @task(1)
    def get_system_metrics(self):
        """
        Fetch system-wide metrics (admin only)
        """
        if not self.token:
            return

        self.client.get("/api/v1/admin/metrics/", name="Get System Metrics (Admin)")

    @task(1)
    def get_user_stats(self):
        """
        Fetch user statistics (admin only)
        """
        if not self.token:
            return

        self.client.get("/api/v1/admin/users/stats/", name="Get User Stats (Admin)")


#############################################
# Event Handlers
#############################################


@events.request.add_hook
def on_request(request_type, name, response_time, response_length, **kwargs):
    """
    Custom event handler for requests
    Can be used for logging or custom metrics
    """
    # Log slow requests
    if response_time > 1000:  # > 1 second
        print(f"SLOW REQUEST: {name} took {response_time}ms")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """
    Called when test starts
    """
    print("=" * 50)
    print("FinanceHub Performance Test Starting")
    print("=" * 50)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Called when test stops
    """
    print("\n" + "=" * 50)
    print("FinanceHub Performance Test Complete")
    print("=" * 50)

    if environment.stats.total.fail_ratio > 0.05:  # 5% failure rate
        print(f"⚠️  WARNING: Failure rate is {environment.stats.total.fail_ratio:.2%}")
    else:
        print(
            f"✅ Failure rate is acceptable: {environment.stats.total.fail_ratio:.2%}"
        )

    print(f"📊 Total requests: {environment.stats.total.num_requests}")
    print(
        f"⏱️  Average response time: {environment.stats.total.avg_response_time:.0f}ms"
    )
    print(f"📈 RPS: {environment.stats.total.total_rps:.2f}")


#############################################
# Weighted User Types
#############################################


# Distribution: 95% regular users, 5% admin users
class WebUser(FinanceHubUser):
    pass


# Custom user classes for different scenarios
class LightUser(FinanceHubUser):
    """Light user - fewer tasks, less realistic"""

    wait_time = between(5, 10)


class HeavyUser(FinanceHubUser):
    """Heavy user - more frequent requests"""

    wait_time = between(0.5, 2)
