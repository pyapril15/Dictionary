"""
app_services package initializer.

This package contains services that interface with external platforms or APIs,
such as GitHub update checking for the Dictionary application.
"""

from .github_service import (
    GitHubUpdateChecker,
    check_for_updates,
    update_for_discontinued,
    is_version_discontinued,
)

__all__ = [
    "GitHubUpdateChecker",
    "check_for_updates",
    "update_for_discontinued",
    "is_version_discontinued",
]
