"""
8Knot API Package
================

Modular API for generating standalone JSON Plotly visualizations and data queries.

This package provides:
- Standalone query functions for all 18 data queries
- Plotly visualization generators for all chart types
- Metrics API for simple counts and aggregations
- Configuration management
- Utility functions for common patterns

Usage:
    from api.queries import AffiliationQuery, CommitsQuery
    from api.visualizations import BarChart, LineChart, PieChart
    from api.metrics import MetricsCalculator
    from api.config import APIConfig
"""

__version__ = "1.0.0"
__author__ = "8Knot Team"

# Import main API classes for easy access
from .config import APIConfig
from .base import BaseQuery, BaseVisualization
from .utils import DateUtils, FormatUtils

__all__ = [
    'APIConfig',
    'BaseQuery', 
    'BaseVisualization',
    'DateUtils',
    'FormatUtils'
] 