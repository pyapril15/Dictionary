"""
GitHub update service for the Dictionary application.

Provides a secure, extensible mechanism to check for updates using the GitHub
Releases API. Implements clean OOP design with abstraction, encapsulation,
and detailed, structured logging.
"""

import sys
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Set, Dict, Any, Callable, Final

import requests

from src.app_logic.app_config import AppConfig
from src.app_logic.log import Log


class AbstractGitHubService(ABC):
    """
    Abstract base class defining the GitHub update service interface.
    """

    @abstractmethod
    def get_latest_release(self) -> Optional[Dict[str, Any]]:
        """
        Fetch the most recent release metadata from GitHub.

        Returns:
            Optional[Dict[str, Any]]: The latest release JSON data if successful, else None.
        """
        pass

    @abstractmethod
    def get_all_versions(self) -> Set[str]:
        """
        Retrieve all available version tags from GitHub releases.

        Returns:
            Set[str]: Set of all version strings, stripped of "v" prefix.
        """
        pass

    @abstractmethod
    def get_update_info(self) -> Tuple[Optional[Dict[str, Any]], Optional[str], Optional[str]]:
        """
        Retrieve release metadata, executable download URL, and version string.

        Returns:
            Tuple[
                Optional[Dict[str, Any]],  # Release JSON
                Optional[str],             # .exe asset download URL
                Optional[str]              # Version string (e.g., "1.2.3")
            ]
        """
        pass


class GitHubUpdateService(AbstractGitHubService):
    """
    Concrete implementation of the AbstractGitHubService using GitHub Releases API.
    Handles communication, response parsing, and asset extraction.
    """

    _DEFAULT_TIMEOUT: Final[int] = 10
    _HEADERS: Final[Dict[str, str]] = {"Accept": "application/vnd.github.v3+json"}

    def __init__(self, log: Log, owner: str = "pyapril15", repo: str = "Dictionary") -> None:
        self._log = log.update
        self._owner = owner
        self._repo = repo
        self._releases_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        self._log.debug(f"GitHubUpdateService initialized for {owner}/{repo}")

    def _get_response(self) -> Optional[requests.Response]:
        """
        Internal helper to perform the GET request to GitHub.

        Returns:
            Optional[requests.Response]: Valid response if successful, else None.
        """
        try:
            self._log.debug(f"Requesting release data from: {self._releases_url}")
            response = requests.get(
                self._releases_url,
                headers=self._HEADERS,
                timeout=self._DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            self._log.error(f"GitHub request error: {e}")
        except Exception as e:
            self._log.exception(f"Unexpected error during GitHub request: {e}")
        return None

    def get_latest_release(self) -> Optional[Dict[str, Any]]:
        self._log.info("Fetching latest GitHub release...")
        response = self._get_response()
        if response:
            releases = response.json()
            self._log.debug(f"{len(releases)} releases retrieved.")
            return releases[0] if releases else None
        return None

    def get_all_versions(self) -> Set[str]:
        self._log.info("Fetching all GitHub release versions...")
        response = self._get_response()
        if response:
            releases = response.json()
            versions = {r["tag_name"].lstrip("v") for r in releases}
            self._log.debug(f"Available versions: {versions}")
            return versions
        return set()

    def get_update_info(self) -> Tuple[Optional[Dict[str, Any]], Optional[str], Optional[str]]:
        self._log.info("Retrieving update information...")
        release = self.get_latest_release()
        if not release:
            self._log.warning("No release data available.")
            return None, None, None

        version = release.get("tag_name", "").lstrip("v")
        self._log.debug(f"Latest version tag: {version}")

        for asset in release.get("assets", []):
            name = asset.get("name", "")
            self._log.debug(f"Examining asset: {name}")
            if name.endswith(".exe"):
                url = asset.get("browser_download_url")
                if url:
                    self._log.info(f"Executable found: {url}")
                    return release, url, version

        self._log.warning("No .exe asset found in latest release.")
        return release, None, version


class UpdateUtility:
    """
    High-level interface for checking updates and handling version management.
    """

    def __init__(self, config: AppConfig, log: Log) -> None:
        self._config = config
        self._log = log.update
        self._github_service = GitHubUpdateService(log)
        self._log.debug("UpdateUtility initialized.")

    def check_for_updates(self, callback: Callable[[Dict[str, Any], str, Tuple[str, str]], None]) -> None:
        """
        Check for a new version and invoke callback if available.

        Args:
            callback (Callable): Function to execute if update is found.
        """
        try:
            current_version = self._config.app_version
            self._log.info(f"Checking for updates (current version: {current_version})")

            release, url, latest_version = self._github_service.get_update_info()
            if not url:
                self._log.warning("No downloadable update found.")
                return

            if latest_version and latest_version > current_version:
                self._log.info(f"Update available: {latest_version}")
                callback(release, url, (current_version, latest_version))
            else:
                self._log.info("Application is up-to-date.")
        except Exception as e:
            self._log.exception(f"Update check failed: {e}")

    def is_version_discontinued(self) -> bool:
        """
        Check if the current version is no longer supported.

        Returns:
            bool: True if the current version is not listed on GitHub.
        """
        try:
            current_version = self._config.app_version
            self._log.info(f"Verifying if version {current_version} is discontinued...")

            versions = self._github_service.get_all_versions()
            discontinued = current_version not in versions

            if discontinued:
                self._log.warning(f"Version {current_version} is discontinued.")
            else:
                self._log.info("Version is still supported.")

            return discontinued
        except Exception as e:
            self._log.exception(f"Discontinued version check failed: {e}")
            return False

    def update_for_discontinued(self, callback: Callable[[Dict[str, Any], str, Tuple[str, str]], None]) -> None:
        """
        Force update path when current version is obsolete or unsupported.

        Args:
            callback (Callable): Function to invoke for update process.
        """
        try:
            current_version = self._config.app_version
            self._log.info(f"Attempting update for discontinued version {current_version}...")

            release, url, latest_version = self._github_service.get_update_info()
            if not url:
                self._log.critical("No valid update found. Exiting application.")
                sys.exit(1)

            callback(release, url, (current_version, latest_version))
        except Exception as e:
            self._log.exception(f"Critical update failure: {e}")
            sys.exit(1)
