"""
8Knot API Visualizations Package
===============================

Standalone Plotly visualization generators for all chart types in the 8Knot system.
Each visualization module provides clean interfaces for generating charts with consistent
styling and behavior.

Available visualization modules:
- AffiliationVisualization: Organization/email domain charts and tables
- CommitVisualization: Commit activity charts and metrics
- IssueVisualization: Issue tracking charts and analysis
- PullRequestVisualization: Pull request analysis charts
- ContributorVisualization: Contributor activity analysis
- RepositoryVisualization: Repository statistics and comparisons
- And more...

Chart types available:
- Bar charts
- Line charts
- Pie charts
- Scatter plots
- Tables
- Time series
- Heatmaps
- Treemaps
"""

from .affiliation_visualization import AffiliationVisualization
from .commit_visualization import CommitVisualization
from .issue_visualization import IssueVisualization
from .pull_request_visualization import PullRequestVisualization
from .contributor_visualization import ContributorVisualization
from .repository_visualization import RepositoryVisualization

__all__ = [
    'AffiliationVisualization',
    'CommitVisualization',
    'IssueVisualization', 
    'PullRequestVisualization',
    'ContributorVisualization',
    'RepositoryVisualization'
] 