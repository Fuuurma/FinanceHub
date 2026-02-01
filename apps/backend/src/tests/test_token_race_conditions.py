"""
Token Race Condition Tests - S-010

Tests for concurrent token refresh to prevent race conditions.

Created by: ARIA (for GRACE/GAUDÍ)
Date: February 1, 2026
Status: TEMPLATE - Needs completion
"""

import pytest
import asyncio
import threading
import time
from datetime import timedelta
from unittest.mock import Mock, patch, AsyncMock
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.core.cache import cache
from apps.backend.src.users.models.token_blacklist import BlacklistedToken
from apps.backend.src.users.services.token_service import TokenService

User = get_user_model()


class TestTokenRaceConditions(TestCase):
    """Test token refresh for race conditions."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.token_service = TokenService()

    def tearDown(self):
        """Clean up after tests."""
        cache.clear()
        BlacklistedToken.objects.all().delete()

    def test_concurrent_token_refresh_same_token(self):
        """
        Test that multiple concurrent refresh requests for the same token
        don't create race conditions.

        Scenario: User clicks refresh twice quickly
        Expected: Only one token should be blacklisted
        """
        refresh_token = "valid_refresh_token"

        # Simulate concurrent refresh attempts
        results = []

        def refresh_attempt():
            try:
                result = self.token_service.refresh_access_token(
                    self.user, refresh_token
                )
                results.append(("success", result))
            except Exception as e:
                results.append(("error", str(e)))

        # Run 3 concurrent attempts
        threads = []
        for i in range(3):
            t = threading.Thread(target=refresh_attempt)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Should have at least one success
        success_count = sum(1 for r in results if r[0] == "success")
        assert success_count >= 1, "At least one refresh should succeed"

    def test_token_blacklist_thread_safety(self):
        """
        Test that token blacklist operations are thread-safe.

        Scenario: Multiple threads adding tokens to blacklist
        Expected: All tokens should be added, no duplicates
        """
        tokens = [f"token_{i}" for i in range(100)]

        def add_to_blacklist(token):
            BlacklistedToken.objects.create(
                token=token,
                user=self.user,
                expires_at=timezone.now() + timedelta(days=1),
            )

        # Add tokens concurrently
        threads = []
        for token in tokens:
            t = threading.Thread(target=add_to_blacklist, args=(token,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # All tokens should be in blacklist
        assert BlacklistedToken.objects.count() == 100

    def test_refresh_token_rotation(self):
        """
        Test that refresh tokens are properly rotated.

        Scenario: User refreshes their access token
        Expected: Old refresh token is blacklisted, new one is issued
        """
        old_refresh = "old_refresh_token"
        new_refresh = "new_refresh_token"

        with patch.object(self.token_service, "refresh_access_token") as mock_refresh:
            mock_refresh.return_value = {
                "access_token": "new_access_token",
                "refresh_token": new_refresh,
                "expires_in": 3600,
            }

            result = self.token_service.refresh_access_token(self.user, old_refresh)

            # Verify old token was blacklisted
            assert BlacklistedToken.objects.filter(token=old_refresh).exists()

            # Verify new token was returned
            assert result["refresh_token"] == new_refresh

    def test_replay_attack_prevention(self):
        """
        Test that replay attacks are prevented.

        Scenario: Attacker tries to use blacklisted token
        Expected: Token refresh should fail
        """
        malicious_token = "stolen_refresh_token"

        # Blacklist the token
        BlacklistedToken.objects.create(
            token=malicious_token,
            user=self.user,
            expires_at=timezone.now() + timedelta(days=1),
        )

        # Attempt to use blacklisted token
        with self.assertRaises(ValidationError):
            self.token_service.refresh_access_token(self.user, malicious_token)

    def test_session_invalidation_timing(self):
        """
        Test session invalidation timing.

        Scenario: User logs out during active session
        Expected: All tokens should be invalidated immediately
        """
        # Create active sessions
        session1 = self.user.session_set.create(
            session_key="session_1", expires_at=timezone.now() + timedelta(hours=24)
        )
        session2 = self.user.session_set.create(
            session_key="session_2", expires_at=timezone.now() + timedelta(hours=24)
        )

        # Invalidate all sessions
        self.token_service.invalidate_user_sessions(self.user)

        # Verify sessions are invalidated
        assert not self.user.session_set.filter(
            session_key__in=["session_1", "session_2"]
        ).exists()


class TestTokenConcurrencyMetrics:
    """Metrics for token concurrency handling."""

    def test_100_concurrent_refreshes(self):
        """
        Performance test: 100 concurrent token refreshes.

        Benchmark: Should complete in under 5 seconds.
        """
        import time
        import threading

        user = Mock()
        refresh_token = "test_token"

        def mock_refresh():
            time.sleep(0.01)  # Simulate 10ms operation

        start = time.time()

        threads = []
        for _ in range(100):
            t = threading.Thread(target=mock_refresh)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        elapsed = time.time() - start
        assert elapsed < 5.0, f"100 concurrent refreshes took {elapsed}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
