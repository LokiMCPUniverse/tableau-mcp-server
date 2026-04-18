"""Configuration for the Tableau MCP server."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TableauConfig(BaseSettings):
    """Runtime configuration for Tableau REST API access.

    Values are loaded from environment variables prefixed with ``TABLEAU_``.
    """

    model_config = SettingsConfigDict(
        env_prefix="TABLEAU_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    server_url: str = Field(
        default="",
        description=(
            "Tableau Server or Tableau Cloud base URL, e.g. "
            "'https://10ax.online.tableau.com' or 'https://tableau.example.com'."
        ),
    )
    api_version: str = Field(default="3.22", description="Tableau REST API version.")
    site_content_url: str = Field(
        default="",
        description="Site content URL; empty string for the default site.",
    )
    pat_name: str = Field(default="", description="Personal Access Token name.")
    pat_secret: str = Field(default="", description="Personal Access Token secret.")
    timeout: float = Field(default=60.0, description="HTTP request timeout in seconds.")

    @property
    def api_base(self) -> str:
        """Fully-qualified REST API base, e.g. ``https://host/api/3.22``."""
        base = self.server_url.rstrip("/")
        return f"{base}/api/{self.api_version}"
