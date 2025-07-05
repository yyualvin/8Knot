"""
8Knot API Commit Metrics
=======================

Simple metric calculators for commit-related statistics including counts,
averages, and activity metrics.
"""

from typing import List, Dict, Any, Union
import logging

from ..base import BaseMetric
from ..queries.commits_query import CommitsQuery
from ..utils import FormatUtils

logger = logging.getLogger(__name__)

class CommitMetrics(BaseMetric):
    """Metric calculator for commit statistics"""
    
    def __init__(self, query_engine: CommitsQuery = None):
        """
        Initialize commit metrics calculator
        
        Args:
            query_engine: CommitsQuery instance
        """
        super().__init__(query_engine or CommitsQuery())
    
    def calculate(self, repo_ids: List[int], **kwargs) -> Union[int, float, str]:
        """
        Calculate default metric (total commits)
        
        Args:
            repo_ids: List of repository IDs
            **kwargs: Additional parameters
            
        Returns:
            Total commit count
        """
        return self.get_total_commits(repo_ids)
    
    def get_total_commits(self, repo_ids: List[int]) -> int:
        """
        Get total commit count
        
        Args:
            repo_ids: List of repository IDs
            
        Returns:
            Total commit count
        """
        return self.query_engine.get_commit_count(repo_ids)
    
    def get_average_lines_added(self, repo_ids: List[int]) -> float:
        """
        Get average lines added per commit
        
        Args:
            repo_ids: List of repository IDs
            
        Returns:
            Average lines added per commit
        """
        stats = self.query_engine.get_commit_stats(repo_ids)
        return stats.get('avg_lines_added', 0.0)
    
    def get_average_lines_removed(self, repo_ids: List[int]) -> float:
        """
        Get average lines removed per commit
        
        Args:
            repo_ids: List of repository IDs
            
        Returns:
            Average lines removed per commit
        """
        stats = self.query_engine.get_commit_stats(repo_ids)
        return stats.get('avg_lines_removed', 0.0)
    
    def get_unique_authors(self, repo_ids: List[int]) -> int:
        """
        Get number of unique authors
        
        Args:
            repo_ids: List of repository IDs
            
        Returns:
            Number of unique authors
        """
        stats = self.query_engine.get_commit_stats(repo_ids)
        return stats.get('unique_authors', 0)
    
    def get_average_files_per_commit(self, repo_ids: List[int]) -> float:
        """
        Get average files changed per commit
        
        Args:
            repo_ids: List of repository IDs
            
        Returns:
            Average files per commit
        """
        return self.query_engine.get_avg_files_per_commit(repo_ids)
    
    def get_commit_metrics_summary(self, repo_ids: List[int]) -> Dict[str, Any]:
        """
        Get comprehensive commit metrics summary
        
        Args:
            repo_ids: List of repository IDs
            
        Returns:
            Dictionary with all commit metrics
        """
        try:
            stats = self.query_engine.get_commit_stats(repo_ids)
            avg_files = self.query_engine.get_avg_files_per_commit(repo_ids)
            
            return {
                "total_commits": stats.get('total_commits', 0),
                "unique_authors": stats.get('unique_authors', 0),
                "avg_lines_added": round(stats.get('avg_lines_added', 0.0), 2),
                "avg_lines_removed": round(stats.get('avg_lines_removed', 0.0), 2),
                "total_lines_added": stats.get('total_lines_added', 0),
                "total_lines_removed": stats.get('total_lines_removed', 0),
                "avg_files_per_commit": round(avg_files, 2),
                "first_commit": stats.get('first_commit'),
                "last_commit": stats.get('last_commit'),
                "formatted_values": {
                    "total_commits": FormatUtils.format_number(stats.get('total_commits', 0)),
                    "unique_authors": FormatUtils.format_number(stats.get('unique_authors', 0)),
                    "avg_lines_added": FormatUtils.format_number(stats.get('avg_lines_added', 0.0)),
                    "avg_lines_removed": FormatUtils.format_number(stats.get('avg_lines_removed', 0.0)),
                    "total_lines_added": FormatUtils.format_number(stats.get('total_lines_added', 0)),
                    "total_lines_removed": FormatUtils.format_number(stats.get('total_lines_removed', 0)),
                    "avg_files_per_commit": FormatUtils.format_number(avg_files)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting commit metrics summary: {str(e)}")
            return {} 