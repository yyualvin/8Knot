"""
8Knot API Metrics Package
========================

Simple metric calculators for counts, averages, and other statistical measures.
These provide quick numerical insights without the overhead of full visualizations.

Available metric modules:
- CommitMetrics: Commit counts, averages, and statistics
- IssueMetrics: Issue counts, age, and resolution statistics
- PullRequestMetrics: Pull request counts, age, and merge statistics
- ContributorMetrics: Contributor counts and activity metrics
- RepositoryMetrics: Repository statistics and comparisons
- AffiliationMetrics: Organization and company affiliation statistics

Each metric class provides:
- Fast numerical calculations
- Formatted display values
- Error handling and validation
- Consistent response structure
"""

from .commit_metrics import CommitMetrics
from .issue_metrics import IssueMetrics
from .pull_request_metrics import PullRequestMetrics
from .contributor_metrics import ContributorMetrics
from .repository_metrics import RepositoryMetrics
from .affiliation_metrics import AffiliationMetrics

__all__ = [
    'CommitMetrics',
    'IssueMetrics',
    'PullRequestMetrics',
    'ContributorMetrics',
    'RepositoryMetrics',
    'AffiliationMetrics'
] 