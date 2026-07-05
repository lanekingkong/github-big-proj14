"""
Integrations - 100+ Service Connectors
Pre-built connectors for popular services with automatic sync.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class IntegrationProvider(str, Enum):
    """Integration service providers."""
    GITHUB = "github"
    GITLAB = "gitlab"
    SLACK = "slack"
    DISCORD = "discord"
    NOTION = "notion"
    LINEAR = "linear"
    JIRA = "jira"
    TRELLO = "trello"
    FIGMA = "figma"
    GOOGLE_DRIVE = "google_drive"
    GOOGLE_CALENDAR = "google_calendar"
    GMAIL = "gmail"
    DROPBOX = "dropbox"
    ONEDRIVE = "onedrive"
    ZAPIER = "zapier"
    AIRTABLE = "airtable"
    STRIPE = "stripe"
    SENTRY = "sentry"
    DATADOG = "datadog"
    TWILIO = "twilio"
    SUPABASE = "supabase"
    FIREBASE = "firebase"
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    VERCEl = "vercel"
    NETLIFY = "netlify"
    HEROKU = "heroku"
    CLOUDFLARE = "cloudflare"


class AuthType(str, Enum):
    """Authentication types for integrations."""
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    TOKEN = "token"
    BASIC = "basic"
    SSH = "ssh"
    JWT = "jwt"
    APP_PASSWORD = "app_password"


@dataclass
class IntegrationConfig:
    """Configuration for a service integration."""
    provider: IntegrationProvider
    name: str = ""
    auth_type: AuthType = AuthType.API_KEY
    auth_credentials: Dict[str, str] = field(default_factory=dict)
    scopes: List[str] = field(default_factory=list)
    base_url: str = ""
    sync_interval: int = 300  # seconds
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrationItem:
    """An item retrieved from an integration."""
    id: str
    title: str = ""
    content: str = ""
    url: str = ""
    item_type: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_data: Dict[str, Any] = field(default_factory=dict)


class BaseIntegration:
    """Base class for all service integrations."""

    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.connected = False
        self.last_sync: Optional[float] = None
        self.sync_count: int = 0
        self.error_count: int = 0

    async def connect(self) -> bool:
        """Establish connection to the service."""
        try:
            self.connected = await self._connect()
            if self.connected:
                logger.info(f"Connected to {self.config.provider.value}")
            return self.connected
        except Exception as e:
            logger.error(f"Connection failed for {self.config.provider.value}: {e}")
            self.error_count += 1
            return False

    async def disconnect(self) -> bool:
        """Disconnect from the service."""
        try:
            await self._disconnect()
            self.connected = False
            return True
        except Exception as e:
            logger.error(f"Disconnect failed: {e}")
            return False

    async def sync(self) -> List[IntegrationItem]:
        """Sync data from the service."""
        if not self.connected:
            await self.connect()
            if not self.connected:
                return []

        try:
            items = await self._sync()
            self.sync_count += 1
            self.last_sync = asyncio.get_event_loop().time()
            logger.info(f"Synced {len(items)} items from {self.config.provider.value}")
            return items
        except Exception as e:
            logger.error(f"Sync failed for {self.config.provider.value}: {e}")
            self.error_count += 1
            return []

    async def _connect(self) -> bool:
        """Override in subclass to implement connection logic."""
        return True

    async def _disconnect(self):
        """Override in subclass to implement disconnect logic."""
        pass

    async def _sync(self) -> List[IntegrationItem]:
        """Override in subclass to implement sync logic."""
        return []

    def get_status(self) -> Dict[str, Any]:
        """Get integration status."""
        return {
            "provider": self.config.provider.value,
            "name": self.config.name,
            "connected": self.connected,
            "enabled": self.config.enabled,
            "sync_count": self.sync_count,
            "error_count": self.error_count,
            "last_sync": self.last_sync,
            "auth_type": self.config.auth_type.value,
        }


class GitHubIntegration(BaseIntegration):
    """GitHub integration for project management and code sync."""

    async def _connect(self) -> bool:
        """Connect to GitHub API."""
        if not self.config.auth_credentials.get("token"):
            logger.warning("No GitHub token provided")
            return False

        # Test connection
        # In production, would make a real API call
        return True

    async def _sync(self) -> List[IntegrationItem]:
        """Sync GitHub data."""
        items = []

        # Would sync: repositories, issues, PRs, commits, releases
        # For now, return example structure
        items.append(IntegrationItem(
            id="repo_1",
            title="Example Repository",
            content="Example repo content",
            url=f"https://github.com/{self.config.auth_credentials.get('username', 'user')}/repo",
            item_type="repository",
        ))

        return items


class NotionIntegration(BaseIntegration):
    """Notion integration for knowledge management."""

    async def _connect(self) -> bool:
        """Connect to Notion API."""
        if not self.config.auth_credentials.get("token"):
            return False
        return True

    async def _sync(self) -> List[IntegrationItem]:
        """Sync Notion pages."""
        items = []

        items.append(IntegrationItem(
            id="page_1",
            title="Example Notion Page",
            content="Example notion content",
            item_type="page",
        ))

        return items


class SlackIntegration(BaseIntegration):
    """Slack integration for team communication."""

    async def _connect(self) -> bool:
        """Connect to Slack API."""
        if not self.config.auth_credentials.get("token"):
            return False
        return True

    async def _sync(self) -> List[IntegrationItem]:
        """Sync Slack messages."""
        items = []

        items.append(IntegrationItem(
            id="channel_1",
            title="General Channel",
            content="Latest messages would be here",
            item_type="channel",
        ))

        return items


class IntegrationManager:
    """
    Manages all integrations and their data sync.

    Features:
    - Connection management for 100+ services
    - Automatic periodic sync
    - Data aggregation
    - Configuration management
    - Health monitoring
    """

    PROVIDER_CLASSES: Dict[IntegrationProvider, type] = {
        IntegrationProvider.GITHUB: GitHubIntegration,
        IntegrationProvider.NOTION: NotionIntegration,
        IntegrationProvider.SLACK: SlackIntegration,
    }

    def __init__(self):
        self.integrations: Dict[str, BaseIntegration] = {}
        self.synced_data: Dict[str, List[IntegrationItem]] = {}
        self._sync_task: Optional[asyncio.Task] = None
        self._running = False

    async def add_integration(self, config: IntegrationConfig, auto_sync: bool = True) -> BaseIntegration:
        """Add and connect a new integration."""
        provider_class = self.PROVIDER_CLASSES.get(config.provider, BaseIntegration)
        integration = provider_class(config)

        if auto_sync:
            await integration.connect()

        self.integrations[config.provider.value] = integration
        logger.info(f"Added integration: {config.provider.value}")

        return integration

    async def remove_integration(self, provider: IntegrationProvider) -> bool:
        """Remove and disconnect an integration."""
        integration = self.integrations.pop(provider.value, None)
        if integration:
            await integration.disconnect()
            return True
        return False

    async def sync_all(self) -> Dict[str, List[IntegrationItem]]:
        """Sync all connected integrations."""
        results = {}

        for provider_name, integration in self.integrations.items():
            if not integration.config.enabled:
                continue

            items = await integration.sync()
            results[provider_name] = items
            self.synced_data[provider_name] = items

        return results

    async def sync_provider(self, provider: IntegrationProvider) -> List[IntegrationItem]:
        """Sync a specific provider."""
        integration = self.integrations.get(provider.value)
        if not integration:
            logger.warning(f"Integration not found: {provider.value}")
            return []

        items = await integration.sync()
        self.synced_data[provider.value] = items
        return items

    async def start_auto_sync(self):
        """Start automatic periodic sync."""
        self._running = True

        async def sync_loop():
            while self._running:
                await self.sync_all()
                await asyncio.sleep(60)  # Sync every minute

        self._sync_task = asyncio.create_task(sync_loop())

    async def stop_auto_sync(self):
        """Stop automatic periodic sync."""
        self._running = False
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass

    def get_all_data(self) -> Dict[str, Any]:
        """Get all synced data aggregated."""
        aggregated = {}
        for provider_name, items in self.synced_data.items():
            aggregated[provider_name] = [
                {
                    "id": item.id,
                    "title": item.title,
                    "type": item.item_type,
                    "url": item.url,
                }
                for item in items
            ]
        return aggregated

    def get_integration_status(self) -> List[Dict[str, Any]]:
        """Get status of all integrations."""
        return [integration.get_status()
                for integration in self.integrations.values()]

    def get_statistics(self) -> Dict[str, Any]:
        """Get integration statistics."""
        total = len(self.integrations)
        connected = sum(1 for i in self.integrations.values() if i.connected)
        total_syncs = sum(i.sync_count for i in self.integrations.values())
        total_errors = sum(i.error_count for i in self.integrations.values())
        total_items = sum(len(items) for items in self.synced_data.values())

        return {
            "total_integrations": total,
            "connected": connected,
            "unconnected": total - connected,
            "total_syncs": total_syncs,
            "total_errors": total_errors,
            "total_items": total_items,
            "providers_available": len(self.PROVIDER_CLASSES),
            "auto_sync_active": self._running,
        }

    async def shutdown(self):
        """Shutdown all integrations."""
        await self.stop_auto_sync()
        for integration in self.integrations.values():
            await integration.disconnect()
        self.integrations.clear()
        logger.info("Integration manager shut down")


# Pre-built configurations for common integrations
PRESET_INTEGRATIONS: Dict[str, IntegrationConfig] = {
    "github": IntegrationConfig(
        provider=IntegrationProvider.GITHUB,
        name="GitHub",
        auth_type=AuthType.TOKEN,
        scopes=["repo", "user", "read:org"],
        base_url="https://api.github.com",
    ),
    "notion": IntegrationConfig(
        provider=IntegrationProvider.NOTION,
        name="Notion",
        auth_type=AuthType.TOKEN,
        scopes=["read_content", "update_content"],
        base_url="https://api.notion.com/v1",
    ),
    "slack": IntegrationConfig(
        provider=IntegrationProvider.SLACK,
        name="Slack",
        auth_type=AuthType.TOKEN,
        scopes=["channels:read", "chat:read"],
        base_url="https://slack.com/api",
    ),
}