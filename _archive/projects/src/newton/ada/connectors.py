"""
Ada Connectors Framework
=========================

Connect to external services and data sources.
Like ChatGPT Connectors but with more flexibility.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field as dataclass_field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type
import json
import os
import re

from .schema import (
    Connector,
    ConnectorType,
)


class ConnectionStatus(Enum):
    """Status of a connector connection."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class ConnectorResult:
    """Result from a connector operation."""

    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = dataclass_field(default_factory=dict)


class BaseConnector(ABC):
    """
    Abstract base class for connectors.

    All connectors must implement these methods.
    """

    connector_type: ConnectorType

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.status = ConnectionStatus.DISCONNECTED
        self._error: Optional[str] = None

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection. Returns True if successful."""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Close connection. Returns True if successful."""
        pass

    @abstractmethod
    def test(self) -> bool:
        """Test the connection. Returns True if working."""
        pass

    @abstractmethod
    def query(self, operation: str, params: Dict[str, Any]) -> ConnectorResult:
        """Execute an operation on the connector."""
        pass

    def get_status(self) -> Dict[str, Any]:
        """Get connector status."""
        return {
            "type": self.connector_type.value,
            "status": self.status.value,
            "error": self._error,
        }


class WebConnector(BaseConnector):
    """
    Connector for web/HTTP operations.

    Supports:
    - Fetching URLs
    - REST API calls
    - Web scraping
    """

    connector_type = ConnectorType.WEB

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.base_url = config.get("base_url") if config else None
        self.headers = config.get("headers", {}) if config else {}
        self.timeout = config.get("timeout", 30) if config else 30

    def connect(self) -> bool:
        """Web connector is always 'connected'."""
        self.status = ConnectionStatus.CONNECTED
        return True

    def disconnect(self) -> bool:
        """Disconnect (no-op for web)."""
        self.status = ConnectionStatus.DISCONNECTED
        return True

    def test(self) -> bool:
        """Test connectivity."""
        try:
            # In production, make a HEAD request to base_url
            self.status = ConnectionStatus.CONNECTED
            return True
        except Exception as e:
            self._error = str(e)
            self.status = ConnectionStatus.ERROR
            return False

    def query(self, operation: str, params: Dict[str, Any]) -> ConnectorResult:
        """
        Execute a web operation.

        Operations:
        - fetch: GET a URL
        - post: POST data
        - search: Search the web
        """
        if operation == "fetch":
            return self._fetch(params.get("url", ""))
        elif operation == "post":
            return self._post(params.get("url", ""), params.get("data", {}))
        elif operation == "search":
            return self._search(params.get("query", ""))
        else:
            return ConnectorResult(
                success=False,
                error=f"Unknown operation: {operation}",
            )

    def _fetch(self, url: str) -> ConnectorResult:
        """Fetch a URL."""
        # In production, use requests library
        # Mock response for demonstration
        return ConnectorResult(
            success=True,
            data={
                "url": url,
                "content": f"Content from {url}",
                "status_code": 200,
            },
            metadata={"fetched_at": datetime.now().isoformat()},
        )

    def _post(self, url: str, data: Dict[str, Any]) -> ConnectorResult:
        """POST data to URL."""
        return ConnectorResult(
            success=True,
            data={
                "url": url,
                "response": {"status": "ok"},
            },
        )

    def _search(self, query: str) -> ConnectorResult:
        """Search the web."""
        # Mock search results
        return ConnectorResult(
            success=True,
            data={
                "query": query,
                "results": [
                    {"title": f"Result 1 for {query}", "url": "https://example.com/1"},
                    {"title": f"Result 2 for {query}", "url": "https://example.com/2"},
                ],
            },
        )


class FileConnector(BaseConnector):
    """
    Connector for local file system operations.

    Supports:
    - Reading files
    - Writing files
    - Directory listing
    - File search
    """

    connector_type = ConnectorType.FILE

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.root_path = config.get("root_path", ".") if config else "."
        self.allowed_extensions = config.get("allowed_extensions") if config else None

    def connect(self) -> bool:
        """Verify root path exists."""
        if os.path.exists(self.root_path):
            self.status = ConnectionStatus.CONNECTED
            return True
        self._error = f"Root path does not exist: {self.root_path}"
        self.status = ConnectionStatus.ERROR
        return False

    def disconnect(self) -> bool:
        """Disconnect (no-op for file system)."""
        self.status = ConnectionStatus.DISCONNECTED
        return True

    def test(self) -> bool:
        """Test file system access."""
        return os.path.exists(self.root_path) and os.access(self.root_path, os.R_OK)

    def query(self, operation: str, params: Dict[str, Any]) -> ConnectorResult:
        """
        Execute a file operation.

        Operations:
        - read: Read a file
        - write: Write a file
        - list: List directory contents
        - search: Search for files
        """
        if operation == "read":
            return self._read(params.get("path", ""))
        elif operation == "write":
            return self._write(params.get("path", ""), params.get("content", ""))
        elif operation == "list":
            return self._list(params.get("path", self.root_path))
        elif operation == "search":
            return self._search(params.get("pattern", "*"))
        else:
            return ConnectorResult(
                success=False,
                error=f"Unknown operation: {operation}",
            )

    def _read(self, path: str) -> ConnectorResult:
        """Read a file."""
        full_path = os.path.join(self.root_path, path)
        try:
            with open(full_path, "r") as f:
                content = f.read()
            return ConnectorResult(
                success=True,
                data={"path": path, "content": content},
            )
        except Exception as e:
            return ConnectorResult(success=False, error=str(e))

    def _write(self, path: str, content: str) -> ConnectorResult:
        """Write to a file."""
        full_path = os.path.join(self.root_path, path)
        try:
            with open(full_path, "w") as f:
                f.write(content)
            return ConnectorResult(
                success=True,
                data={"path": path, "bytes_written": len(content)},
            )
        except Exception as e:
            return ConnectorResult(success=False, error=str(e))

    def _list(self, path: str) -> ConnectorResult:
        """List directory contents."""
        full_path = os.path.join(self.root_path, path) if path != self.root_path else path
        try:
            entries = os.listdir(full_path)
            files = []
            dirs = []
            for entry in entries:
                entry_path = os.path.join(full_path, entry)
                if os.path.isdir(entry_path):
                    dirs.append(entry)
                else:
                    files.append(entry)
            return ConnectorResult(
                success=True,
                data={"path": path, "files": files, "directories": dirs},
            )
        except Exception as e:
            return ConnectorResult(success=False, error=str(e))

    def _search(self, pattern: str) -> ConnectorResult:
        """Search for files matching pattern."""
        import fnmatch
        matches = []
        for root, dirs, files in os.walk(self.root_path):
            for filename in fnmatch.filter(files, pattern):
                rel_path = os.path.relpath(os.path.join(root, filename), self.root_path)
                matches.append(rel_path)
        return ConnectorResult(
            success=True,
            data={"pattern": pattern, "matches": matches},
        )


class APIConnector(BaseConnector):
    """
    Connector for REST API integrations.

    Supports:
    - Generic REST API calls
    - Authentication handling
    - Rate limiting
    """

    connector_type = ConnectorType.API

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.base_url = config.get("base_url") if config else None
        self.api_key = config.get("api_key") if config else None
        self.auth_header = config.get("auth_header", "Authorization") if config else "Authorization"
        self.rate_limit = config.get("rate_limit", 60) if config else 60  # requests per minute
        self._request_count = 0
        self._last_reset = datetime.now()

    def connect(self) -> bool:
        """Verify API connectivity."""
        if not self.base_url:
            self._error = "No base URL configured"
            self.status = ConnectionStatus.ERROR
            return False

        # Test the connection
        if self.test():
            self.status = ConnectionStatus.CONNECTED
            return True
        return False

    def disconnect(self) -> bool:
        """Disconnect from API."""
        self.status = ConnectionStatus.DISCONNECTED
        return True

    def test(self) -> bool:
        """Test API connectivity."""
        try:
            # In production, make a test request
            self.status = ConnectionStatus.CONNECTED
            return True
        except Exception as e:
            self._error = str(e)
            self.status = ConnectionStatus.ERROR
            return False

    def query(self, operation: str, params: Dict[str, Any]) -> ConnectorResult:
        """
        Execute an API operation.

        Operations:
        - get: GET request
        - post: POST request
        - put: PUT request
        - delete: DELETE request
        """
        # Check rate limit
        if not self._check_rate_limit():
            return ConnectorResult(
                success=False,
                error="Rate limit exceeded",
            )

        endpoint = params.get("endpoint", "")
        data = params.get("data", {})

        if operation == "get":
            return self._request("GET", endpoint, data)
        elif operation == "post":
            return self._request("POST", endpoint, data)
        elif operation == "put":
            return self._request("PUT", endpoint, data)
        elif operation == "delete":
            return self._request("DELETE", endpoint, data)
        else:
            return ConnectorResult(
                success=False,
                error=f"Unknown operation: {operation}",
            )

    def _request(self, method: str, endpoint: str, data: Dict[str, Any]) -> ConnectorResult:
        """Make an HTTP request."""
        # In production, use requests library
        # Mock response for demonstration
        self._request_count += 1

        return ConnectorResult(
            success=True,
            data={
                "method": method,
                "endpoint": endpoint,
                "response": {"status": "ok", "data": data},
            },
            metadata={
                "url": f"{self.base_url}/{endpoint}",
                "timestamp": datetime.now().isoformat(),
            },
        )

    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limit."""
        now = datetime.now()
        if (now - self._last_reset).total_seconds() >= 60:
            self._request_count = 0
            self._last_reset = now
        return self._request_count < self.rate_limit


class ConnectorRegistry:
    """
    Registry of available connectors.

    Manages connector lifecycle and provides
    unified access to all connected services.
    """

    # Built-in connector types
    CONNECTOR_TYPES: Dict[ConnectorType, Type[BaseConnector]] = {
        ConnectorType.WEB: WebConnector,
        ConnectorType.FILE: FileConnector,
        ConnectorType.API: APIConnector,
    }

    def __init__(self):
        self._connectors: Dict[str, BaseConnector] = {}
        self._configs: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        name: str,
        connector_type: ConnectorType,
        config: Dict[str, Any] = None,
    ) -> BaseConnector:
        """
        Register and create a connector.

        Args:
            name: Unique name for this connector
            connector_type: Type of connector
            config: Connector configuration

        Returns:
            Created connector
        """
        if name in self._connectors:
            raise ValueError(f"Connector '{name}' already exists")

        connector_class = self.CONNECTOR_TYPES.get(connector_type)
        if not connector_class:
            raise ValueError(f"Unknown connector type: {connector_type}")

        connector = connector_class(config)
        self._connectors[name] = connector
        self._configs[name] = config or {}

        return connector

    def get(self, name: str) -> Optional[BaseConnector]:
        """Get a connector by name."""
        return self._connectors.get(name)

    def remove(self, name: str) -> bool:
        """Remove a connector."""
        if name in self._connectors:
            connector = self._connectors[name]
            if connector.status == ConnectionStatus.CONNECTED:
                connector.disconnect()
            del self._connectors[name]
            del self._configs[name]
            return True
        return False

    def list_connectors(self) -> List[Dict[str, Any]]:
        """List all connectors with their status."""
        return [
            {
                "name": name,
                **connector.get_status(),
            }
            for name, connector in self._connectors.items()
        ]

    def connect_all(self) -> Dict[str, bool]:
        """Connect all connectors."""
        results = {}
        for name, connector in self._connectors.items():
            results[name] = connector.connect()
        return results

    def disconnect_all(self) -> Dict[str, bool]:
        """Disconnect all connectors."""
        results = {}
        for name, connector in self._connectors.items():
            results[name] = connector.disconnect()
        return results

    def query(
        self,
        connector_name: str,
        operation: str,
        params: Dict[str, Any],
    ) -> ConnectorResult:
        """
        Execute a query on a connector.

        Args:
            connector_name: Name of the connector
            operation: Operation to perform
            params: Operation parameters

        Returns:
            ConnectorResult
        """
        connector = self._connectors.get(connector_name)
        if not connector:
            return ConnectorResult(
                success=False,
                error=f"Connector not found: {connector_name}",
            )

        if connector.status != ConnectionStatus.CONNECTED:
            return ConnectorResult(
                success=False,
                error=f"Connector not connected: {connector_name}",
            )

        return connector.query(operation, params)

    def register_custom_connector(
        self,
        connector_type: ConnectorType,
        connector_class: Type[BaseConnector],
    ):
        """Register a custom connector class."""
        self.CONNECTOR_TYPES[connector_type] = connector_class

    def save_configs(self, filepath: str):
        """Save connector configurations."""
        # Exclude sensitive data
        safe_configs = {}
        for name, config in self._configs.items():
            safe_configs[name] = {
                k: v for k, v in config.items()
                if k not in ("api_key", "password", "token", "secret")
            }
            safe_configs[name]["_type"] = self._connectors[name].connector_type.value

        with open(filepath, "w") as f:
            json.dump(safe_configs, f, indent=2)

    def load_configs(self, filepath: str):
        """Load connector configurations."""
        with open(filepath, "r") as f:
            configs = json.load(f)

        for name, config in configs.items():
            connector_type = ConnectorType(config.pop("_type"))
            self.register(name, connector_type, config)
