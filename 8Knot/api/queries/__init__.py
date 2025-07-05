"""
8Knot API Queries Package
========================

Standalone query functions for all data queries in the 8Knot system.
Each query module provides a clean interface for fetching data from the database.

Available query modules:
- AffiliationQuery: Organization/email domain analysis
- CommitsQuery: Commit activity and statistics
- ContributorsQuery: Contributor activity analysis
- IssuesQuery: Issue tracking and metrics
- PullRequestsQuery: Pull request analysis
- RepositoryQuery: Repository information and statistics
- And more...
"""

from .affiliation_query import AffiliationQuery
from .commits_query import CommitsQuery
from .contributors_query import ContributorsQuery
from .issues_query import IssuesQuery
from .pull_requests_query import PullRequestsQuery
from .repository_query import RepositoryQuery

__all__ = [
    'AffiliationQuery',
    'CommitsQuery', 
    'ContributorsQuery',
    'IssuesQuery',
    'PullRequestsQuery',
    'RepositoryQuery'
] 