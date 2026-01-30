import pytest
from datetime import datetime


def test_homepage_loads(page):
    """Test that the homepage loads successfully."""
    page.goto("http://localhost:3000")
    assert page.title() == "FinanceHub"


def test_navigation_works(page):
    """Test that main navigation links work."""
    page.goto("http://localhost:3000")

    # Test Dashboard link
    page.click('text=Dashboard')
    assert page.url == "http://localhost:3000/dashboard"

    # Test Portfolio link
    page.click('text=Portfolio')
    assert page.url == "http://localhost:3000/portfolio"


def test_login_flow(page):
    """Test user login flow."""
    page.goto("http://localhost:3000/login")

    # Fill in login form
    page.fill('input[name="email"]', 'test@example.com')
    page.fill('input[name="password"]', 'testpass123')
    page.click('button[type="submit"]')

    # Should redirect to dashboard
    assert page.url == "http://localhost:3000/dashboard"
    assert page.locator('text=Welcome').count() > 0


def test_portfolio_page_loads(page):
    """Test portfolio page loads with data."""
    page.goto("http://localhost:3000/login")
    page.fill('input[name="email"]', 'test@example.com')
    page.fill('input[name="password"]', 'testpass123')
    page.click('button[type="submit"]')

    page.goto("http://localhost:3000/portfolio")

    # Check that portfolio data is displayed
    assert page.locator('text=Total Value').count() > 0
    assert page.locator('text=Holdings').count() > 0


def test_api_health(page, request):
    """Test API health endpoint."""
    response = request.get("http://localhost:3000/api/health")
    assert response.status == 200
    assert response.json()["status"] == "healthy"


def test_realtime_chart_loads(page):
    """Test that realtime chart loads."""
    page.goto("http://localhost:3000/login")
    page.fill('input[name="email"]', 'test@example.com')
    page.fill('input[name="password"]', 'testpass123')
    page.click('button[type="submit"]')

    page.goto("http://localhost:3000/dashboard")

    # Check for chart canvas
    assert page.locator('canvas').count() > 0


def test_responsive_design(page):
    """Test responsive design on mobile."""
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto("http://localhost:3000")

    # Check mobile menu is present
    assert page.locator('[aria-label="Menu"]').count() > 0
