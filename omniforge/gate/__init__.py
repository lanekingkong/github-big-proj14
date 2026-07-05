"""
Gateway - API Gateway and Service Router
Manages all external service connections and API routing.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import aiohttp
from aiohttp import ClientSession, ClientTimeout

logger = logging.getLogger(__name__)


class ServiceType(str, Enum):
    """Types of external services."""
    API = "api"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"
    STORAGE = "storage"
    AUTH = "auth"
    NOTIFICATION = "notification"
    PAYMENT = "payment"
    AI_MODEL = "ai_model"
    SEARCH = "search"
    CACHE = "cache"


class ServiceStatus(str, Enum):
    """Service connection status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


@dataclass
class ServiceEndpoint:
    """Definition of a service endpoint."""
    name: str
    url: str
    service_type: ServiceType
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    retry_count: int = 3
    rate_limit: Optional[int] = None
    requires_auth: bool = False
    auth_type: str = "bearer"
    description: str = ""


@dataclass
class ServiceResponse:
    """Standardized service response."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    latency_ms: Optional[float] = None
    endpoint: Optional[str] = None
    retry_count: int = 0


@dataclass
class ServiceHealth:
    """Health status of a service."""
    endpoint: str
    status: ServiceStatus
    latency_ms: float
    last_check: float
    error_rate: float = 0.0
    uptime: float = 1.0
    details: Dict[str, Any] = field(default_factory=dict)


class CircuitBreaker:
    """
    Circuit breaker pattern for service resilience.

    Prevents cascading failures by temporarily disabling
    services that are failing repeatedly.
    """

    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time = 0
        self.state = "closed"  # closed, open, half-open

    def record_success(self):
        """Record a successful call."""
        self.failures = 0
        self.state = "closed"

    def record_failure(self):
        """Record a failed call."""
        self.failures += 1
        self.last_failure_time = time.time()

        if self.failures >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker opened after {self.failures} failures")

    def can_execute(self) -> bool:
        """Check if the circuit allows execution."""
        if self.state == "closed":
            return True
        elif self.state == "open":
            # Check if reset timeout has passed
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = "half-open"
                return True
            return False
        else:  # half-open
            return True

    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status."""
        return {
            "state": self.state,
            "failures": self.failures,
            "last_failure": self.last_failure_time,
            "threshold": self.failure_threshold,
            "reset_timeout": self.reset_timeout,
        }


class RateLimiter:
    """Rate limiting for service calls."""

    def __init__(self, requests_per_second: int = 10):
        self.requests_per_second = requests_per_second
        self.request_times: List[float] = []

    def can_make_request(self) -> bool:
        """Check if a new request can be made."""
        now = time.time()
        # Remove old requests
        self.request_times = [t for t in self.request_times
                             if now - t < 1.0]

        if len(self.request_times) < self.requests_per_second:
            self.request_times.append(now)
            return True
        return False

    def wait_time(self) -> float:
        """Calculate wait time until next request can be made."""
        if len(self.request_times) < self.requests_per_second:
            return 0.0

        oldest = min(self.request_times)
        return max(0.0, 1.0 - (time.time() - oldest))


class Gateway:
    """
    API Gateway for managing all external service connections.

    Features:
    - Service discovery and routing
    - Circuit breaking for resilience
    - Rate limiting and throttling
    - Request/response transformation
    - Authentication and authorization
    - Health monitoring
    - Caching
    - Load balancing
    """

    def __init__(self, base_url: str = "", session: Optional[ClientSession] = None):
        self.base_url = base_url.rstrip("/")
        self.session = session
        self.endpoints: Dict[str, ServiceEndpoint] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.rate_limiters: Dict[str, RateLimiter] = {}
        self.health_checks: Dict[str, ServiceHealth] = {}
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.cache_ttl = 300  # 5 minutes
        self._session_created = False

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def initialize(self):
        """Initialize the gateway."""
        if not self.session:
            timeout = ClientTimeout(total=30)
            self.session = ClientSession(timeout=timeout)
            self._session_created = True

        logger.info("Gateway initialized")

    async def close(self):
        """Close the gateway and cleanup resources."""
        if self.session and self._session_created:
            await self.session.close()
            self.session = None
            logger.info("Gateway closed")

    def register_endpoint(self, endpoint: ServiceEndpoint):
        """Register a service endpoint."""
        self.endpoints[endpoint.name] = endpoint

        # Initialize circuit breaker and rate limiter
        if endpoint.name not in self.circuit_breakers:
            self.circuit_breakers[endpoint.name] = CircuitBreaker()

        if endpoint.rate_limit:
            self.rate_limiters[endpoint.name] = RateLimiter(endpoint.rate_limit)

        logger.info(f"Registered endpoint: {endpoint.name} ({endpoint.service_type.value})")

    async def call(self, endpoint_name: str, **kwargs) -> ServiceResponse:
        """
        Call a registered service endpoint.

        Args:
            endpoint_name: Name of the registered endpoint
            **kwargs: Additional parameters for the request

        Returns:
            ServiceResponse with standardized format
        """
        endpoint = self.endpoints.get(endpoint_name)
        if not endpoint:
            return ServiceResponse(
                success=False,
                error=f"Endpoint '{endpoint_name}' not found",
            )

        # Check circuit breaker
        cb = self.circuit_breakers.get(endpoint_name)
        if cb and not cb.can_execute():
            return ServiceResponse(
                success=False,
                error=f"Circuit breaker open for {endpoint_name}",
            )

        # Check rate limiter
        rl = self.rate_limiters.get(endpoint_name)
        if rl and not rl.can_make_request():
            wait_time = rl.wait_time()
            if wait_time > 0:
                await asyncio.sleep(wait_time)

        # Build request
        url = self._build_url(endpoint, kwargs)
        headers = self._build_headers(endpoint, kwargs)
        data = self._build_data(endpoint, kwargs)

        # Check cache
        cache_key = self._get_cache_key(endpoint_name, kwargs)
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return ServiceResponse(
                    success=True,
                    data=cached_data,
                    endpoint=endpoint_name,
                )

        # Make request
        start_time = time.time()
        try:
            async with self.session.request(
                method=endpoint.method,
                url=url,
                headers=headers,
                json=data if endpoint.method in ["POST", "PUT", "PATCH"] else None,
                params=data if endpoint.method == "GET" else None,
                timeout=endpoint.timeout,
            ) as response:
                latency_ms = (time.time() - start_time) * 1000

                # Parse response
                if response.status < 400:
                    response_data = await self._parse_response(response)
                    result = ServiceResponse(
                        success=True,
                        data=response_data,
                        status_code=response.status,
                        latency_ms=latency_ms,
                        endpoint=endpoint_name,
                    )

                    # Record success
                    if cb:
                        cb.record_success()

                    # Update health
                    self._update_health(endpoint_name, latency_ms, True)

                    # Cache successful responses
                    if endpoint.method == "GET" and response.status == 200:
                        self.cache[cache_key] = (response_data, time.time())

                    return result
                else:
                    error_text = await response.text()
                    result = ServiceResponse(
                        success=False,
                        error=f"HTTP {response.status}: {error_text[:200]}",
                        status_code=response.status,
                        latency_ms=latency_ms,
                        endpoint=endpoint_name,
                    )

                    # Record failure
                    if cb:
                        cb.record_failure()

                    self._update_health(endpoint_name, latency_ms, False)
                    return result

        except asyncio.TimeoutError:
            latency_ms = (time.time() - start_time) * 1000
            result = ServiceResponse(
                success=False,
                error=f"Timeout after {endpoint.timeout}s",
                latency_ms=latency_ms,
                endpoint=endpoint_name,
            )

            if cb:
                cb.record_failure()
            self._update_health(endpoint_name, latency_ms, False)
            return result

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            result = ServiceResponse(
                success=False,
                error=str(e),
                latency_ms=latency_ms,
                endpoint=endpoint_name,
            )

            if cb:
                cb.record_failure()
            self._update_health(endpoint_name, latency_ms, False)
            return result

    def _build_url(self, endpoint: ServiceEndpoint, kwargs: Dict) -> str:
        """Build the full URL for a request."""
        url = endpoint.url

        # Replace path parameters
        for key, value in kwargs.items():
            if f"{{{key}}}" in url:
                url = url.replace(f"{{{key}}}", str(value))

        # Add base URL if not absolute
        if not urlparse(url).netloc and self.base_url:
            url = f"{self.base_url}/{url.lstrip('/')}"

        return url

    def _build_headers(self, endpoint: ServiceEndpoint, kwargs: Dict) -> Dict[str, str]:
        """Build request headers."""
        headers = endpoint.headers.copy()

        # Add authentication headers
        if endpoint.requires_auth and "auth_token" in kwargs:
            if endpoint.auth_type == "bearer":
                headers["Authorization"] = f"Bearer {kwargs['auth_token']}"
            elif endpoint.auth_type == "api_key":
                headers["X-API-Key"] = kwargs["auth_token"]

        # Add content type for JSON requests
        if endpoint.method in ["POST", "PUT", "PATCH"]:
            headers.setdefault("Content-Type", "application/json")

        return headers

    def _build_data(self, endpoint: ServiceEndpoint, kwargs: Dict) -> Optional[Dict]:
        """Build request data/body."""
        # Remove special keys
        data_keys = {k: v for k, v in kwargs.items()
                    if k not in ["auth_token", "cache_key"]}

        # For GET requests, return as params
        if endpoint.method == "GET":
            return data_keys

        # For other methods, return as JSON body
        return data_keys if data_keys else None

    async def _parse_response(self, response) -> Any:
        """Parse the HTTP response."""
        content_type = response.headers.get("Content-Type", "")

        if "application/json" in content_type:
            return await response.json()
        elif "text/" in content_type:
            return await response.text()
        else:
            return await response.read()

    def _get_cache_key(self, endpoint_name: str, kwargs: Dict) -> str:
        """Generate a cache key for the request."""
        key_data = {
            "endpoint": endpoint_name,
            "params": {k: v for k, v in kwargs.items() if k != "auth_token"},
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def _update_health(self, endpoint_name: str, latency_ms: float, success: bool):
        """Update health status for an endpoint."""
        now = time.time()

        if endpoint_name not in self.health_checks:
            self.health_checks[endpoint_name] = ServiceHealth(
                endpoint=endpoint_name,
                status=ServiceStatus.HEALTHY,
                latency_ms=latency_ms,
                last_check=now,
                error_rate=0.0,
                uptime=1.0,
            )

        health = self.health_checks[endpoint_name]
        health.last_check = now
        health.latency_ms = latency_ms

        # Update error rate (simple moving average)
        if not success:
            health.error_rate = (health.error_rate * 0.9) + 0.1
        else:
            health.error_rate = health.error_rate * 0.9

        # Update status based on metrics
        if health.error_rate > 0.5:
            health.status = ServiceStatus.UNHEALTHY
        elif health.error_rate > 0.2:
            health.status = ServiceStatus.DEGRADED
        elif latency_ms > 1000:
            health.status = ServiceStatus.DEGRADED
        else:
            health.status = ServiceStatus.HEALTHY

    async def health_check_all(self) -> Dict[str, ServiceHealth]:
        """Perform health checks on all endpoints."""
        results = {}

        for endpoint_name in self.endpoints:
            # Simple ping check
            try:
                start_time = time.time()
                async with self.session.head(self.endpoints[endpoint_name].url) as response:
                    latency_ms = (time.time() - start_time) * 1000
                    success = response.status < 400

                    self._update_health(endpoint_name, latency_ms, success)
                    results[endpoint_name] = self.health_checks[endpoint_name]
            except Exception as e:
                logger.warning(f"Health check failed for {endpoint_name}: {e}")
                self._update_health(endpoint_name, 10000, False)
                results[endpoint_name] = self.health_checks[endpoint_name]

        return results

    def get_endpoint_status(self, endpoint_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed status for an endpoint."""
        if endpoint_name not in self.endpoints:
            return None

        endpoint = self.endpoints[endpoint_name]
        cb_status = self.circuit_breakers.get(endpoint_name, {}).get_status()
        health = self.health_checks.get(endpoint_name)

        return {
            "endpoint": endpoint_name,
            "url": endpoint.url,
            "type": endpoint.service_type.value,
            "method": endpoint.method,
            "requires_auth": endpoint.requires_auth,
            "circuit_breaker": cb_status,
            "health": health.__dict__ if health else None,
            "rate_limit": endpoint.rate_limit,
        }

    def clear_cache(self, endpoint_name: Optional[str] = None):
        """Clear the cache for an endpoint or all endpoints."""
        if endpoint_name:
            # Clear all cache keys for this endpoint
            keys_to_remove = [k for k in self.cache.keys()
                             if k.startswith(hashlib.md5(endpoint_name.encode()).hexdigest()[:8])]
            for key in keys_to_remove:
                del self.cache[key]
            logger.info(f"Cleared cache for {endpoint_name}")
        else:
            self.cache.clear()
            logger.info("Cleared all cache")

    def get_statistics(self) -> Dict[str, Any]:
        """Get gateway statistics."""
        total_endpoints = len(self.endpoints)
        healthy_endpoints = sum(1 for h in self.health_checks.values()
                               if h.status == ServiceStatus.HEALTHY)

        cache_size = len(self.cache)
        cache_hit_rate = 0.0  # Would need tracking for actual rate

        return {
            "total_endpoints": total_endpoints,
            "healthy_endpoints": healthy_endpoints,
            "unhealthy_endpoints": total_endpoints - healthy_endpoints,
            "cache_size": cache_size,
            "cache_ttl": self.cache_ttl,
            "circuit_breakers": len(self.circuit_breakers),
            "rate_limiters": len(self.rate_limiters),
        }


# Pre-configured service endpoints for common APIs
COMMON_SERVICES = {
    "openai_chat": ServiceEndpoint(
        name="openai_chat",
        url="https://api.openai.com/v1/chat/completions",
        service_type=ServiceType.AI_MODEL,
        method="POST",
        requires_auth=True,
        auth_type="bearer",
        description="OpenAI Chat Completions API",
    ),
    "github_api": ServiceEndpoint(
        name="github_api",
        url="https://api.github.com",
        service_type=ServiceType.API,
        method="GET",
        headers={"Accept": "application/vnd.github.v3+json"},
        description="GitHub REST API",
    ),
    "weather_api": ServiceEndpoint(
        name="weather_api",
        url="https://api.open-meteo.com/v1/forecast",
        service_type=ServiceType.API,
        method="GET",
        description="Open-Meteo Weather API",
    ),
    "currency_api": ServiceEndpoint(
        name="currency_api",
        url="https://api.exchangerate-api.com/v4/latest/USD",
        service_type=ServiceType.API,
        method="GET",
        description="Exchange Rate API",
    ),
}