"""
Dashboard - Web-based Project Management UI
Real-time monitoring and control panel for OmniForge projects.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DashboardWidget:
    """A widget on the dashboard."""
    id: str
    title: str
    widget_type: str  # chart, table, status, metric, log, etc.
    data: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0, "width": 4, "height": 3})
    config: Dict[str, Any] = field(default_factory=dict)
    refresh_interval: int = 30  # seconds


@dataclass
class DashboardLayout:
    """Dashboard layout configuration."""
    id: str
    name: str
    widgets: List[DashboardWidget] = field(default_factory=list)
    theme: str = "dark"
    auto_refresh: bool = True
    refresh_interval: int = 30


class DashboardServer:
    """
    Web-based dashboard server for OmniForge.

    Provides:
    - Real-time project monitoring
    - Agent team visualization
    - Workflow progress tracking
    - Resource usage metrics
    - Integration status
    - Log viewer
    - Configuration management
    """

    def __init__(self, host: str = "localhost", port: int = 8520):
        self.host = host
        self.port = port
        self.layouts: Dict[str, DashboardLayout] = {}
        self.metrics: Dict[str, List[Dict[str, Any]]] = {}
        self._initialized = False

    async def initialize(self):
        """Initialize the dashboard server."""
        # Create default layout
        default_layout = DashboardLayout(
            id="default",
            name="Default Dashboard",
            widgets=[
                DashboardWidget(
                    id="project_health",
                    title="Project Health",
                    widget_type="metric",
                    data={},
                    position={"x": 0, "y": 0, "width": 4, "height": 2},
                ),
                DashboardWidget(
                    id="agent_status",
                    title="Agent Status",
                    widget_type="status",
                    data={},
                    position={"x": 4, "y": 0, "width": 4, "height": 2},
                ),
                DashboardWidget(
                    id="workflow_progress",
                    title="Workflow Progress",
                    widget_type="chart",
                    data={},
                    position={"x": 8, "y": 0, "width": 4, "height": 2},
                ),
                DashboardWidget(
                    id="integration_health",
                    title="Integration Health",
                    widget_type="status",
                    data={},
                    position={"x": 0, "y": 2, "width": 4, "height": 2},
                ),
                DashboardWidget(
                    id="recent_logs",
                    title="Recent Activity",
                    widget_type="log",
                    data={},
                    position={"x": 4, "y": 2, "width": 8, "height": 3},
                ),
                DashboardWidget(
                    id="resource_usage",
                    title="Resource Usage",
                    widget_type="chart",
                    data={},
                    position={"x": 0, "y": 4, "width": 6, "height": 2},
                ),
                DashboardWidget(
                    id="cost_tracking",
                    title="Cost Tracking",
                    widget_type="metric",
                    data={},
                    position={"x": 6, "y": 4, "width": 6, "height": 2},
                ),
            ],
        )
        self.layouts["default"] = default_layout
        self._initialized = True
        logger.info(f"Dashboard initialized on {self.host}:{self.port}")

    async def start(self):
        """Start the dashboard server."""
        if not self._initialized:
            await self.initialize()

        # In production, would start a web server (FastAPI/aiohttp)
        logger.info(f"Dashboard server starting on http://{self.host}:{self.port}")
        # TODO: Implement actual web server
        # This is a stub - the actual server would be implemented
        # using FastAPI or aiohttp for the web interface

    async def stop(self):
        """Stop the dashboard server."""
        logger.info("Dashboard server stopped")

    def add_widget(self, layout_id: str, widget: DashboardWidget):
        """Add a widget to a layout."""
        layout = self.layouts.get(layout_id)
        if layout:
            layout.widgets.append(widget)

    def remove_widget(self, layout_id: str, widget_id: str):
        """Remove a widget from a layout."""
        layout = self.layouts.get(layout_id)
        if layout:
            layout.widgets = [w for w in layout.widgets if w.id != widget_id]

    def update_widget(self, layout_id: str, widget_id: str, data: Dict[str, Any]):
        """Update widget data."""
        layout = self.layouts.get(layout_id)
        if layout:
            for widget in layout.widgets:
                if widget.id == widget_id:
                    widget.data.update(data)

    def record_metric(self, name: str, value: Any, timestamp: Optional[datetime] = None):
        """Record a metric value."""
        if name not in self.metrics:
            self.metrics[name] = []

        self.metrics[name].append({
            "value": value,
            "timestamp": (timestamp or datetime.now()).isoformat(),
        })

        # Keep only last 1000 entries
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]

    def get_metrics(self, name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recorded metrics."""
        metrics = self.metrics.get(name, [])
        return metrics[-limit:] if metrics else []

    def get_dashboard_data(self, layout_id: str = "default") -> Dict[str, Any]:
        """Get all data for dashboard rendering."""
        layout = self.layouts.get(layout_id)
        if not layout:
            return {"error": f"Layout '{layout_id}' not found"}

        return {
            "layout": {
                "id": layout.id,
                "name": layout.name,
                "theme": layout.theme,
                "auto_refresh": layout.auto_refresh,
                "refresh_interval": layout.refresh_interval,
            },
            "widgets": [
                {
                    "id": w.id,
                    "title": w.title,
                    "type": w.widget_type,
                    "data": w.data,
                    "position": w.position,
                }
                for w in layout.widgets
            ],
            "timestamp": datetime.now().isoformat(),
        }

    def export_dashboard(self, layout_id: str = "default") -> str:
        """Export dashboard configuration as JSON."""
        layout = self.layouts.get(layout_id)
        if not layout:
            return json.dumps({"error": f"Layout '{layout_id}' not found"})

        return json.dumps(self.get_dashboard_data(layout_id), indent=2)

    def import_dashboard(self, layout_json: str) -> Optional[str]:
        """Import dashboard configuration from JSON."""
        try:
            data = json.loads(layout_json)
            layout_id = data.get("layout", {}).get("id", "imported")

            layout = DashboardLayout(
                id=layout_id,
                name=data.get("layout", {}).get("name", "Imported Layout"),
                theme=data.get("layout", {}).get("theme", "dark"),
                auto_refresh=data.get("layout", {}).get("auto_refresh", True),
                refresh_interval=data.get("layout", {}).get("refresh_interval", 30),
            )

            for widget_data in data.get("widgets", []):
                widget = DashboardWidget(
                    id=widget_data["id"],
                    title=widget_data["title"],
                    widget_type=widget_data["type"],
                    position=widget_data.get("position", {"x": 0, "y": 0, "width": 4, "height": 3}),
                )
                layout.widgets.append(widget)

            self.layouts[layout_id] = layout
            return layout_id
        except Exception as e:
            logger.error(f"Failed to import dashboard: {e}")
            return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get dashboard statistics."""
        return {
            "layouts_count": len(self.layouts),
            "total_widgets": sum(len(l.widgets) for l in self.layouts.values()),
            "metrics_categories": len(self.metrics),
            "total_metrics": sum(len(v) for v in self.metrics.values()),
            "uptime": "running" if self._initialized else "stopped",
        }


# HTML template for the dashboard
DASHBOARD_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OmniForge Dashboard</title>
<style>
:root {
    --bg: #0d1117;
    --bg-secondary: #161b22;
    --border: #30363d;
    --text: #e6edf3;
    --text-secondary: #8b949e;
    --accent: #58a6ff;
    --success: #3fb950;
    --warning: #d29922;
    --danger: #f85149;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
}
header {
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
    padding: 16px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
header h1 { font-size: 1.25rem; font-weight: 600; }
main {
    padding: 24px;
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: 16px;
}
.widget {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
}
.widget h3 {
    font-size: 0.875rem;
    color: var(--text-secondary);
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent);
}
.status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-right: 4px;
}
.status-dot.healthy { background: var(--success); }
.status-dot.warning { background: var(--warning); }
.status-dot.error { background: var(--danger); }
.col-4 { grid-column: span 4; }
.col-6 { grid-column: span 6; }
.col-8 { grid-column: span 8; }
.col-12 { grid-column: span 12; }
</style>
</head>
<body>
<header>
    <h1>OmniForge Dashboard</h1>
    <span id="status">Connected</span>
</header>
<main id="dashboard">
    <!-- Widgets rendered dynamically -->
</main>
<script>
// Dashboard WebSocket client
const ws = new WebSocket(`ws://${location.host}/ws`);
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateDashboard(data);
};

function updateDashboard(data) {
    // Update widgets dynamically
    data.widgets.forEach(w => {
        const el = document.getElementById(w.id);
        if (el) {
            el.querySelector('.widget-content').innerHTML = renderWidget(w);
        }
    });
}

function renderWidget(widget) {
    // Render widget based on type
    switch(widget.type) {
        case 'metric':
            return `<div class="metric-value">${widget.data.value || 'N/A'}</div>`;
        case 'status':
            return widget.data.items?.map(i =>
                `<div><span class="status-dot ${i.status}"></span>${i.name}: ${i.value}</div>`
            ).join('') || '';
        default:
            return JSON.stringify(widget.data);
    }
}
</script>
</body>
</html>"""