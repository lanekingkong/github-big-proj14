"""
Utilities - Common helper functions and tools
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import re
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

logger = logging.getLogger(__name__)

T = TypeVar("T")


def safe_path(path: Union[str, Path]) -> Path:
    """Convert string to Path and resolve safely."""
    if isinstance(path, str):
        path = Path(path)
    return path.resolve()


def ensure_dir(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if not."""
    path = safe_path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def hash_content(content: str) -> str:
    """Create a content-based hash."""
    return hashlib.md5(content.encode()).hexdigest()


def sanitize_filename(filename: str) -> str:
    """Make a string safe for use as a filename."""
    # Remove invalid characters
    safe = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Trim spaces
    safe = safe.strip()
    # Limit length
    if len(safe) > 255:
        name, ext = os.path.splitext(safe)
        safe = name[:255 - len(ext)] + ext
    return safe or "untitled"


def format_timestamp(dt: Optional[datetime] = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a datetime to string."""
    dt = dt or datetime.now()
    return dt.strftime(fmt)


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse a timestamp string."""
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M",
        "%m/%d/%Y %H:%M",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue

    return None


def chunk_list(items: List[T], chunk_size: int) -> List[List[T]]:
    """Split a list into chunks."""
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge multiple dictionaries."""
    result = {}

    for d in dicts:
        for key, value in d.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_dicts(result[key], value)
            else:
                result[key] = value

    return result


def truncate_string(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate a string to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text."""
    url_pattern = re.compile(
        r'https?://[^\s<>"\'()]+|'
        r'www\.[^\s<>"\'()]+'
    )
    return url_pattern.findall(text)


def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL."""
    url_pattern = re.compile(
        r'^https?://'
        r'[\w\-]+(\.[\w\-]+)+'
        r'(:\d+)?'
        r'(/[\w\-\.~:/?#\[\]@!$&\'()*+,;=]*)?$'
    )
    return bool(url_pattern.match(url))


async def retry_async(func: Callable, max_retries: int = 3,
                      delay: float = 1.0, backoff: float = 2.0,
                      exceptions: tuple = (Exception,)) -> Any:
    """Retry an async function with exponential backoff."""
    last_exception = None

    for attempt in range(max_retries):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")

            if attempt < max_retries - 1:
                await asyncio.sleep(delay * (backoff ** attempt))

    raise last_exception


class Timer:
    """Context manager for timing operations."""

    def __init__(self, name: str = "operation"):
        self.name = name
        self.start_time = 0.0
        self.elapsed = 0.0

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, *args):
        self.elapsed = time.time() - self.start_time
        logger.debug(f"{self.name} took {self.elapsed:.2f}s")


class RateLimiter:
    """Simple rate limiter for function calls."""

    def __init__(self, calls_per_second: float = 10.0):
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0.0

    async def wait(self):
        """Wait if needed to respect rate limit."""
        now = time.time()
        elapsed = now - self.last_call

        if elapsed < self.min_interval:
            await asyncio.sleep(self.min_interval - elapsed)

        self.last_call = time.time()


class LRUCache:
    """Simple LRU cache implementation."""

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache: Dict[str, Any] = {}
        self.access_order: List[str] = []

    def get(self, key: str) -> Optional[Any]:
        """Get a value, moving to end (most recently used)."""
        if key in self.cache:
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None

    def set(self, key: str, value: Any):
        """Set a value, evicting oldest if needed."""
        if key in self.cache:
            self.access_order.remove(key)

        self.cache[key] = value
        self.access_order.append(key)

        # Evict if over capacity
        while len(self.cache) > self.max_size:
            oldest = self.access_order.pop(0)
            del self.cache[oldest]

    def clear(self):
        """Clear the cache."""
        self.cache.clear()
        self.access_order.clear()

    def __len__(self) -> int:
        return len(self.cache)

    def __contains__(self, key: str) -> bool:
        return key in self.cache


class ConfigManager:
    """Configuration file manager."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(os.path.expanduser("~")) / ".omniforge" / "config.json"
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.data: Dict[str, Any] = {}
        self.load()

    def load(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                logger.warning("Invalid config file, using defaults")
                self.data = {}
        return self.data

    def save(self):
        """Save configuration to file."""
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        keys = key.split(".")
        value = self.data

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """Set a configuration value."""
        keys = key.split(".")
        target = self.data

        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]

        target[keys[-1]] = value
        self.save()

    def delete(self, key: str):
        """Delete a configuration key."""
        keys = key.split(".")
        target = self.data

        for k in keys[:-1]:
            if k in target:
                target = target[k]
            else:
                return

        if keys[-1] in target:
            del target[keys[-1]]
            self.save()

    def to_dict(self) -> Dict[str, Any]:
        """Get all configuration as dict."""
        return self.data.copy()


def create_project_structure(base_path: Path, project_name: str, module_names: Optional[List[str]] = None) -> Path:
    """Create standard project directory structure."""
    project_path = base_path / project_name
    project_path.mkdir(parents=True, exist_ok=True)

    # Standard directories
    directories = [
        "src",
        "tests",
        "docs",
        "scripts",
        "data",
        "config",
        "logs",
        "assets",
        "examples",
        ".github/workflows",
        ".vscode",
    ]

    directories += module_names or []

    for directory in directories:
        (project_path / directory).mkdir(parents=True, exist_ok=True)

    return project_path


def get_project_info(project_path: Path) -> Dict[str, Any]:
    """Get project information."""
    info = {
        "path": str(project_path),
        "name": project_path.name,
        "exists": project_path.exists(),
    }

    if project_path.exists():
        # Count files
        total_files = 0
        total_size = 0
        file_types: Dict[str, int] = {}

        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                total_files += 1
                total_size += file_path.stat().st_size
                ext = file_path.suffix or "no_ext"
                file_types[ext] = file_types.get(ext, 0) + 1

        info["total_files"] = total_files
        info["total_size"] = total_size
        info["file_types"] = file_types
        info["last_modified"] = format_timestamp(datetime.fromtimestamp(project_path.stat().st_mtime))

    return info


def validate_project_name(name: str) -> bool:
    """Validate a project name."""
    if not name or len(name) > 100:
        return False

    # Check for valid Python package name
    pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')
    return bool(pattern.match(name))


class EventEmitter:
    """Simple event emitter for decoupled communication."""

    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def on(self, event: str, callback: Callable):
        """Register an event listener."""
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)

    def off(self, event: str, callback: Callable):
        """Remove an event listener."""
        if event in self._listeners:
            self._listeners[event] = [cb for cb in self._listeners[event] if cb != callback]

    async def emit(self, event: str, *args, **kwargs):
        """Emit an event to all listeners."""
        if event in self._listeners:
            for callback in self._listeners[event]:
                try:
                    await callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Event handler error for '{event}': {e}")

    def clear(self):
        """Remove all listeners."""
        self._listeners.clear()