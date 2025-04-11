"""
GitHub update service for the Dictionary application.

This module provides functionality to interact with the GitHub API for:
- Fetching the latest release version.
- Comparing against the current app version.
- Downloading new update metadata.
- Handling version discontinuation.

The GitHub repository used is defined by the `_owner` and `_repo` constants.
"""

import sys
import requests
from typing import Optional, Tuple, Set, Dict, Any, Callable

from src.app_logic import Log
from src.app_logic import AppConfig


class GitHubUpdateChecker:
    """Checks GitHub for available application updates."""

    _owner: str = "pyapril15"
    _repo: str = "Dictionary"
    _releases_url: str = f"https://api.github.com/repos/{_owner}/{_repo}/releases"

    @classmethod
    def get_latest_release(cls) -> Optional[Dict[str, Any]]:
        """
        Returns the latest release information from GitHub.

        :return: A dictionary representing the latest release, or None if not available.
        """
        try:
            Log.info("Fetching latest release...")

            response = requests.get(cls._releases_url)
            response.raise_for_status()
            releases = response.json()

            return releases[0] if releases else None
        except requests.RequestException as e:
            Log.error(f"Failed to fetch latest release: {str(e)}")
            return None

    @classmethod
    def get_all_versions(cls) -> Set[str]:
        """
        Retrieves all version tags from GitHub releases.

        :return: A set of version strings.
        """
        try:
            Log.info("Fetching all available versions...")
            response = requests.get(cls._releases_url)
            response.raise_for_status()
            return {release["tag_name"].lstrip("v") for release in response.json()}
        except requests.RequestException as e:
            Log.error(f"Error fetching versions: {str(e)}")
            return set()

    @classmethod
    def get_update_info(cls) -> Tuple[Optional[Dict[str, Any]], Optional[str], Optional[str]]:
        """
        Returns update details including the release object, download URL, and version.

        :return: A tuple of (release_info, .exe download URL, version string).
        """
        try:
            release = cls.get_latest_release()
            if release:
                version = release["tag_name"].lstrip("v")
                for asset in release.get("assets", []):
                    if asset["name"].endswith(".exe"):
                        Log.info(f"Update found for version {version}")
                        return release, asset["browser_download_url"], version

            Log.warning("No .exe asset found in any release.")
            return None, None, None
        except requests.RequestException as e:
            Log.error(f"Error retrieving update info: {str(e)}")
            return None, None, None


def check_for_updates(config: AppConfig, callback) -> None:
    """
    Checks for updates on GitHub and triggers a callback if a newer version is found.

    :param config: AppConfig object containing the current version.
    :param callback: Function to call when an update is available. Receives (release_info, url, (current, latest)).
    """
    current_version = config.app_version
    release_info, update_url, latest_version = GitHubUpdateChecker.get_update_info()

    if not update_url:
        Log.warning("No downloadable update found.")
        return

    if latest_version and latest_version > current_version:
        Log.info(f"New version available: {latest_version}")
        callback(release_info, update_url, (current_version, latest_version))
    else:
        Log.info("You already have the latest version.")


def update_for_discontinued(config: AppConfig, callback) -> None:
    """
    Handles upgrade if the current version is discontinued.

    :param config: AppConfig object with current version.
    :param callback: Callback to trigger if an update is available.
    """
    current_version = config.app_version
    release_info, update_url, latest_version = GitHubUpdateChecker.get_update_info()

    if not update_url:
        Log.critical("No update found to replace discontinued version.")
        sys.exit(1)

    callback(release_info, update_url, (current_version, latest_version))


def is_version_discontinued(config: AppConfig) -> bool:
    """
    Determines whether the current version is discontinued (not found in GitHub releases).

    :param config: AppConfig with the current version.
    :return: True if the version is discontinued, otherwise False.
    """
    available_versions = GitHubUpdateChecker.get_all_versions()
    discontinued = config.app_version not in available_versions
    if discontinued:
        Log.warning(f"Version {config.app_version} is discontinued.")
    return discontinued
