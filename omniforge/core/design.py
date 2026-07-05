"""
Design System Intelligence
Professional UI generation with brand consistency and AI-aware design tokens.

Inspired by Awesome Design MD and Impeccable design systems.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

logger = logging.getLogger(__name__)


class DesignStyle(str, Enum):
    """Pre-configured design styles from popular brands."""
    LINEAR = "linear"
    STRIPE = "stripe"
    VERCEl = "vercel"
    NOTION = "notion"
    APPLE = "apple"
    GITHUB = "github"
    SHOPIFY = "shopify"
    AIRBNB = "airbnb"
    SPOTIFY = "spotify"
    CUSTOM = "custom"

    @classmethod
    def from_name(cls, name: str) -> "DesignStyle":
        """Get or create a DesignStyle from name."""
        try:
            return cls(name.lower())
        except ValueError:
            return cls.CUSTOM


@dataclass
class ColorPalette:
    """Color system definition."""
    primary: str = "#5E6AD2"
    primary_hover: str = "#4F5BC5"
    primary_light: str = "#E8EAFC"
    secondary: str = "#6B7280"
    success: str = "#10B981"
    warning: str = "#F59E0B"
    error: str = "#EF4444"
    background: str = "#FFFFFF"
    surface: str = "#F9FAFB"
    surface_hover: str = "#F3F4F6"
    border: str = "#E5E7EB"
    text_primary: str = "#111827"
    text_secondary: str = "#6B7280"
    text_tertiary: str = "#9CA3AF"


@dataclass
class Typography:
    """Typography system definition."""
    font_family: str = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    font_mono: str = "JetBrains Mono, Fira Code, monospace"
    h1_size: str = "2.25rem"
    h2_size: str = "1.875rem"
    h3_size: str = "1.5rem"
    h4_size: str = "1.25rem"
    body_size: str = "1rem"
    small_size: str = "0.875rem"
    line_height: float = 1.6


@dataclass
class Spacing:
    """Spacing system definition."""
    xs: str = "0.25rem"
    sm: str = "0.5rem"
    md: str = "1rem"
    lg: str = "1.5rem"
    xl: str = "2rem"
    xxl: str = "3rem"
    section: str = "4rem"


@dataclass
class BorderRadius:
    """Border radius definitions."""
    sm: str = "0.25rem"
    md: str = "0.5rem"
    lg: str = "0.75rem"
    xl: str = "1rem"
    full: str = "9999px"


@dataclass
class Shadows:
    """Shadow definitions."""
    sm: str = "0 1px 2px rgba(0,0,0,0.05)"
    md: str = "0 4px 6px rgba(0,0,0,0.07)"
    lg: str = "0 10px 25px rgba(0,0,0,0.1)"
    xl: str = "0 20px 50px rgba(0,0,0,0.15)"


@dataclass
class Animation:
    """Animation definitions."""
    duration_fast: str = "150ms"
    duration_normal: str = "250ms"
    duration_slow: str = "350ms"
    easing: str = "cubic-bezier(0.4, 0, 0.2, 1)"
    easing_bounce: str = "cubic-bezier(0.68, -0.55, 0.265, 1.55)"


@dataclass
class DesignConfig:
    """Complete design configuration."""
    style: DesignStyle = DesignStyle.LINEAR
    colors: ColorPalette = field(default_factory=ColorPalette)
    typography: Typography = field(default_factory=Typography)
    spacing: Spacing = field(default_factory=Spacing)
    radius: BorderRadius = field(default_factory=BorderRadius)
    shadows: Shadows = field(default_factory=Shadows)
    animation: Animation = field(default_factory=Animation)
    dark_mode: bool = False
    responsive_breakpoints: Dict[str, int] = field(default_factory=lambda: {
        "sm": 640,
        "md": 768,
        "lg": 1024,
        "xl": 1280,
        "xxl": 1536,
    })

    def dict(self) -> Dict[str, Any]:
        return {
            "style": self.style.value,
            "colors": self.colors.__dict__,
            "typography": self.typography.__dict__,
            "spacing": self.spacing.__dict__,
            "radius": self.radius.__dict__,
            "shadows": self.shadows.__dict__,
            "animation": self.animation.__dict__,
            "dark_mode": self.dark_mode,
        }


# Pre-built design systems (inspired by Awesome Design MD)
PRESET_DESIGNS: Dict[DesignStyle, Dict[str, Any]] = {
    DesignStyle.LINEAR: {
        "colors": ColorPalette(
            primary="#5E6AD2", primary_hover="#4F5BC5",
            background="#FCFCFC", surface="#F4F4F5",
            text_primary="#18181B",
        ),
        "typography": Typography(
            font_family="Inter, SF Pro, -apple-system, sans-serif",
        ),
        "description": "Clean, minimal, and highly functional. Used by Linear for project management.",
    },
    DesignStyle.VERCEl: {
        "colors": ColorPalette(
            primary="#000000", primary_hover="#333333",
            background="#FFFFFF", surface="#FAFAFA",
            text_primary="#000000",
        ),
        "typography": Typography(
            font_family="Geist, Inter, -apple-system, sans-serif",
            font_mono="Geist Mono, JetBrains Mono, monospace",
        ),
        "description": "Dark and minimal with high contrast. Vercel's signature design language.",
    },
    DesignStyle.STRIPE: {
        "colors": ColorPalette(
            primary="#635BFF", primary_hover="#5851DB",
            background="#FFFFFF", surface="#F7F7F8",
            text_primary="#1A1F36",
        ),
        "typography": Typography(
            font_family="Inter, -apple-system, BlinkMacSystemFont, sans-serif",
        ),
        "description": "Professional and trustworthy. Stripe's polished design system.",
    },
    DesignStyle.NOTION: {
        "colors": ColorPalette(
            primary="#37352F", primary_hover="#2F2F2F",
            background="#FFFFFF", surface="#FBFBFA",
            text_primary="#37352F",
            border="#E9E9E7",
        ),
        "typography": Typography(
            font_family="Inter, ui-sans-serif, -apple-system, sans-serif",
        ),
        "description": "Minimal, text-focused design. Notion's clean aesthetic.",
    },
    DesignStyle.APPLE: {
        "colors": ColorPalette(
            primary="#0071E3", primary_hover="#0077ED",
            background="#FFFFFF", surface="#F5F5F7",
            text_primary="#1D1D1F",
        ),
        "typography": Typography(
            font_family="SF Pro Display, SF Pro Text, -apple-system, sans-serif",
        ),
        "radius": BorderRadius(lg="0.75rem", xl="1.125rem"),
        "description": "Premium, refined, and accessible. Apple's Human Interface Guidelines.",
    },
    DesignStyle.GITHUB: {
        "colors": ColorPalette(
            primary="#2DA44E", primary_hover="#2C974B",
            background="#FFFFFF", surface="#F6F8FA",
            text_primary="#1F2328",
        ),
        "typography": Typography(
            font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        ),
        "description": "Developer-friendly and functional. GitHub's design system.",
    },
}


class DesignSystem:
    """
    AI-aware design intelligence system.

    Key features:
    - Pre-built design systems from top brands
    - Automatic design token generation
    - AI-friendly design configuration format
    - Dark mode support
    - Responsive design helpers
    - Component style generation
    """

    def __init__(self, style: DesignStyle = DesignStyle.LINEAR,
                 auto_optimize: bool = True):
        self.style = style
        self.auto_optimize = auto_optimize
        self.config = DesignConfig(style=style)
        self._project_styles: Dict[str, Dict[str, Any]] = {}
        self._component_styles: Dict[str, Dict[str, Any]] = {}

    async def initialize(self) -> None:
        """Load pre-built design systems."""
        # Load preset for the selected style
        if self.style in PRESET_DESIGNS:
            preset = PRESET_DESIGNS[self.style]
            for key, value in preset.items():
                if key != "description" and hasattr(self.config, key):
                    setattr(self.config, key, value)

        # Build component styles
        self._build_component_styles()
        logger.info(f"Design system initialized with style: {self.style.value}")

    def set_project_style(self, project_name: str, preferences: Dict[str, Any]) -> None:
        """Apply custom design preferences for a project."""
        config = DesignConfig(style=self.style)

        # Override with project preferences
        if "colors" in preferences:
            for key, value in preferences["colors"].items():
                if hasattr(config.colors, key):
                    setattr(config.colors, key, value)

        if "typography" in preferences:
            for key, value in preferences["typography"].items():
                if hasattr(config.typography, key):
                    setattr(config.typography, key, value)

        self._project_styles[project_name] = config.dict()
        logger.info(f"Applied custom design for project: {project_name}")

    def get_project_design(self, project_name: str) -> Dict[str, Any]:
        """Get design configuration for a project."""
        return self._project_styles.get(project_name, self.config.dict())

    def generate_design_md(self, style: Optional[DesignStyle] = None) -> str:
        """
        Generate a DESIGN.md file for AI coding agents.

        This creates a markdown document that AI agents can read
        to generate consistent, professional UI components.
        """
        s = style or self.style
        config = self.config

        if s in PRESET_DESIGNS:
            preset = PRESET_DESIGNS[s]
            colors = preset.get("colors", config.colors)
            typography = preset.get("typography", config.typography)
        else:
            colors = config.colors
            typography = config.typography

        md = f"""# DESIGN.md - {s.value.title()} Style Design System

> This file defines the complete design system for AI coding agents.
> Follow these rules strictly when generating any UI components.

## Color System

### Primary Colors
- Primary: `{colors.primary}` - Main actions, links, brand elements
- Primary Hover: `{colors.primary_hover}` - Hover state for primary elements
- Primary Light: `{colors.primary_light}` - Light backgrounds, tags, badges

### Semantic Colors
- Success: `{colors.success}` - Confirmations, success states
- Warning: `{colors.warning}` - Warnings, caution states
- Error: `{colors.error}` - Errors, destructive actions, danger zones

### Neutral Colors
- Background: `{colors.background}` - Page background
- Surface: `{colors.surface}` - Card backgrounds, elevated surfaces
- Border: `{colors.border}` - Dividers, borders, separators
- Text Primary: `{colors.text_primary}` - Headings, body text
- Text Secondary: `{colors.text_secondary}` - Descriptions, captions

## Typography

- Font Family: `{typography.font_family}`
- Mono Font: `{typography.font_mono}`

### Text Sizes
- H1: {typography.h1_size} (weight: 700)
- H2: {typography.h2_size} (weight: 600)
- H3: {typography.h3_size} (weight: 600)
- H4: {typography.h4_size} (weight: 500)
- Body: {typography.body_size} (weight: 400)
- Small: {typography.small_size} (weight: 400)
- Line Height: {typography.line_height}

## Spacing Scale
- XS: {self.config.spacing.xs}
- SM: {self.config.spacing.sm}
- MD: {self.config.spacing.md}
- LG: {self.config.spacing.lg}
- XL: {self.config.spacing.xl}
- XXL: {self.config.spacing.xxl}

## Border Radius
- SM: {self.config.radius.sm} (buttons, inputs)
- MD: {self.config.radius.md} (cards, dialogs)
- LG: {self.config.radius.lg} (modals)
- Full: {self.config.radius.full} (pills, badges)

## Shadows
- SM: `{self.config.shadows.sm}` - Cards, subtle elevation
- MD: `{self.config.shadows.md}` - Dropdowns, tooltips
- LG: `{self.config.shadows.lg}` - Modals, dialogs

## Animation
- Fast: {self.config.animation.duration_fast}
- Normal: {self.config.animation.duration_normal}
- Slow: {self.config.animation.duration_slow}
- Easing: {self.config.animation.easing}

## Component Rules

### Buttons
- Primary: bg=primary, text=white, radius=md, padding=md
- Secondary: bg=surface, text=text primary, border=border
- Use hover states: hover:bg=primary-hover
- Disabled: opacity=0.5, cursor=not-allowed

### Inputs
- Border color: border (focus: primary)
- Padding: md
- Radius: sm
- Background: background
- Label: text secondary, small size

### Cards
- Background: surface
- Border: 1px solid border
- Radius: md
- Padding: lg
- Shadow: sm

### Layout
- Max content width: 1200px (for desktop)
- Content padding: responsive (16px mobile, 32px desktop)
- Section spacing: 4rem between major sections
- Grid gap: md to lg depending on density

## Accessibility
- Minimum contrast ratio: 4.5:1 for text
- Focus indicators on all interactive elements
- Proper ARIA labels and roles
- Keyboard navigation support

## Responsive Design
- Mobile: < 640px (single column, full-width)
- Tablet: 640-1024px (2 columns)
- Desktop: > 1024px (multi-column, max-width container)

---
*Generated by OmniForge Design System Intelligence*
"""
        return md

    def generate_css_variables(self) -> str:
        """Generate CSS custom properties from the design config."""
        config = self.config
        css = """:root {
  /* Colors */
  --color-primary: {{config.colors.primary}};
  --color-primary-hover: {{config.colors.primary_hover}};
  --color-primary-light: {{config.colors.primary_light}};
  --color-secondary: {{config.colors.secondary}};
  --color-success: {{config.colors.success}};
  --color-warning: {{config.colors.warning}};
  --color-error: {{config.colors.error}};
  --color-background: {{config.colors.background}};
  --color-surface: {{config.colors.surface}};
  --color-border: {{config.colors.border}};
  --color-text-primary: {{config.colors.text_primary}};
  --color-text-secondary: {{config.colors.text_secondary}};

  /* Typography */
  --font-family: {{config.typography.font_family}};
  --font-mono: {{config.typography.font_mono}};
  --font-size-h1: {{config.typography.h1_size}};
  --font-size-h2: {{config.typography.h2_size}};
  --font-size-h3: {{config.typography.h3_size}};
  --font-size-body: {{config.typography.body_size}};
  --font-size-small: {{config.typography.small_size}};
  --line-height: {{config.typography.line_height}};

  /* Spacing */
  --spacing-xs: {{config.spacing.xs}};
  --spacing-sm: {{config.spacing.sm}};
  --spacing-md: {{config.spacing.md}};
  --spacing-lg: {{config.spacing.lg}};
  --spacing-xl: {{config.spacing.xl}};
  --spacing-xxl: {{config.spacing.xxl}};

  /* Border Radius */
  --radius-sm: {{config.radius.sm}};
  --radius-md: {{config.radius.md}};
  --radius-lg: {{config.radius.lg}};

  /* Shadows */
  --shadow-sm: {{config.shadows.sm}};
  --shadow-md: {{config.shadows.md}};
  --shadow-lg: {{config.shadows.lg}};

  /* Animation */
  --transition-fast: {{config.animation.duration_fast}};
  --transition-normal: {{config.animation.duration_normal}};
  --transition-slow: {{config.animation.duration_slow}};
  --easing: {{config.animation.easing}};
}
"""
        # Replace placeholders with actual values
        for field_name in ["colors", "typography", "spacing", "radius", "shadows", "animation"]:
            field = getattr(config, field_name)
            for attr_name in dir(field):
                if not attr_name.startswith("_"):
                    placeholder = f"{{{{config.{field_name}.{attr_name}}}}}"
                    css = css.replace(placeholder, str(getattr(field, attr_name, "")))

        return css

    def _build_component_styles(self) -> None:
        """Build CSS classes for common UI components."""
        config = self.config
        self._component_styles = {
            "button_primary": {
                "background": config.colors.primary,
                "color": "#FFFFFF",
                "border": "none",
                "padding": f"{config.spacing.sm} {config.spacing.lg}",
                "border_radius": config.radius.md,
                "cursor": "pointer",
                "font_weight": "500",
                "transition": f"all {config.animation.duration_fast} {config.animation.easing}",
            },
            "card": {
                "background": config.colors.surface,
                "border": f"1px solid {config.colors.border}",
                "border_radius": config.radius.md,
                "padding": config.spacing.lg,
                "box_shadow": config.shadows.sm,
            },
            "input": {
                "background": config.colors.background,
                "border": f"1px solid {config.colors.border}",
                "border_radius": config.radius.sm,
                "padding": config.spacing.md,
                "font_size": config.typography.body_size,
                "color": config.colors.text_primary,
            },
            "container": {
                "max_width": "1200px",
                "margin": "0 auto",
                "padding": f"0 {config.spacing.md}",
            },
        }

    def get_component_style(self, component: str) -> Dict[str, Any]:
        """Get a pre-built component style."""
        return self._component_styles.get(component, {})

    def auto_evaluate_ui(self, html_content: str) -> Dict[str, Any]:
        """
        Automatically evaluate UI quality based on design system rules.
        Returns a report with issues and suggestions.
        """
        issues = []
        suggestions = []

        config = self.config

        # Check color consistency
        if config.colors.primary.lower() not in html_content.lower():
            issues.append({
                "type": "color_consistency",
                "severity": "medium",
                "message": "Primary brand color not found in UI",
            })
            suggestions.append(f"Use primary color {config.colors.primary} for main actions")

        # Check font usage
        if config.typography.font_family.split(",")[0].strip() not in html_content:
            issues.append({
                "type": "typography",
                "severity": "low",
                "message": "Primary font not detected",
            })

        # Check accessibility
        if '<button' in html_content and 'aria-label' not in html_content:
            issues.append({
                "type": "accessibility",
                "severity": "high",
                "message": "Buttons missing ARIA labels",
            })
            suggestions.append("Add aria-label attributes to all buttons")

        return {
            "score": max(0, 100 - len(issues) * 10),
            "issues": issues,
            "suggestions": suggestions,
            "passed": len(issues) == 0,
        }

    def list_available_styles(self) -> List[Dict[str, str]]:
        """List all available pre-built design styles."""
        return [
            {"name": style.value, "description": PRESET_DESIGNS[style].get("description", "")}
            for style in PRESET_DESIGNS
        ]

    def switch_style(self, style: DesignStyle) -> None:
        """Switch to a different design style."""
        self.style = style
        if style in PRESET_DESIGNS:
            preset = PRESET_DESIGNS[style]
            for key, value in preset.items():
                if key != "description" and hasattr(self.config, key):
                    setattr(self.config, key, value)
        self._build_component_styles()
        logger.info(f"Switched to design style: {style.value}")