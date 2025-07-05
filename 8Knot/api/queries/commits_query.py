"""
8Knot API Commits Query
======================

Query functions for commit data including commit activity, author information,
file changes, and commit statistics.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import logging
from datetime import datetime, date

from ..base import BaseQuery
from ..utils import DataUtils, FormatUtils, DateUtils

logger = logging.getLogger(__name__)

class CommitsQuery(BaseQuery):
    """Query engine for commit data"""
    
    def get_data(self, repo_ids: List[int], **kwargs) -> pd.DataFrame:
        """
        Get commit data for repositories
        
        Args:
            repo_ids: List of repository IDs
            **kwargs: Additional parameters
            
        Returns:
            DataFrame with commit data
        """
        return self.get_commits(repo_ids, **kwargs)
    
    def get_commits(self, repo_ids: List[int], limit: Optional[int] = None) -> pd.DataFrame:
        """
        Get commit data for repositories
        
        Args:
            repo_ids: List of repository IDs
            limit: Maximum number of records to return
            
        Returns:
            DataFrame with commit data
        """
        if not repo_ids:
            return pd.DataFrame()
            
        repo_ids_str = self.format_repo_ids_for_sql(repo_ids)
        limit_clause = f"LIMIT {limit}" if limit else ""
        
        query = f"""
            SELECT
                DISTINCT
                r.repo_id,
                c.cmt_commit_hash AS commit_hash,
                c.cmt_author_email AS author_email,
                c.cmt_author_date AS author_date,
                timezone('utc', c.cmt_author_timestamp) AS author_timestamp,
                timezone('utc', c.cmt_committer_timestamp) AS committer_timestamp,
                c.cmt_author_name AS author_name,
                c.cmt_committer_name AS committer_name,
                c.cmt_added AS lines_added,
                c.cmt_removed AS lines_removed
            FROM
                repo r
            JOIN commits c
                ON r.repo_id = c.repo_id
            WHERE
                c.repo_id in ({repo_ids_str})
                AND timezone('utc', c.cmt_author_timestamp) < now()
                AND timezone('utc', c.cmt_committer_timestamp) < now()
            ORDER BY c.cmt_author_timestamp DESC
            {limit_clause}
        """
        
        return self.execute_query(query)
    
    def get_commit_count(self, repo_ids: List[int]) -> int:
        """
        Get total commit count for repositories
        
        Args:
            repo_ids: List of repository IDs
            
        Returns:
            Total commit count
        """
        if not repo_ids:
            return 0
            
        repo_ids_str = self.format_repo_ids_for_sql(repo_ids)
        
        query = f"""
            SELECT COUNT(DISTINCT c.cmt_commit_hash) as commit_count
            FROM commits c
            WHERE c.repo_id in ({repo_ids_str})
        """
        
        df = self.execute_query(query)
        return df.iloc[0]['commit_count'] if not df.empty else 0
    
    def get_commit_stats(self, repo_ids: List[int]) -> Dict[str, Any]:
        """
        Get commit statistics for repositories
        
        Args:
            repo_ids: List of repository IDs
            
        Returns:
            Dictionary with commit statistics
        """
        if not repo_ids:
            return {}
            
        repo_ids_str = self.format_repo_ids_for_sql(repo_ids)
        
        query = f"""
            SELECT 
                COUNT(DISTINCT c.cmt_commit_hash) as total_commits,
                COUNT(DISTINCT c.cmt_author_email) as unique_authors,
                AVG(c.cmt_added) as avg_lines_added,
                AVG(c.cmt_removed) as avg_lines_removed,
                SUM(c.cmt_added) as total_lines_added,
                SUM(c.cmt_removed) as total_lines_removed,
                MIN(c.cmt_author_timestamp) as first_commit,
                MAX(c.cmt_author_timestamp) as last_commit
            FROM commits c
            WHERE c.repo_id in ({repo_ids_str})
        """
        
        df = self.execute_query(query)
        
        if df.empty:
            return {}
            
        row = df.iloc[0]
        return {
            "total_commits": int(row['total_commits']) if row['total_commits'] else 0,
            "unique_authors": int(row['unique_authors']) if row['unique_authors'] else 0,
            "avg_lines_added": float(row['avg_lines_added']) if row['avg_lines_added'] else 0.0,
            "avg_lines_removed": float(row['avg_lines_removed']) if row['avg_lines_removed'] else 0.0,
            "total_lines_added": int(row['total_lines_added']) if row['total_lines_added'] else 0,
            "total_lines_removed": int(row['total_lines_removed']) if row['total_lines_removed'] else 0,
            "first_commit": row['first_commit'],
            "last_commit": row['last_commit']
        }
    
    def get_commits_over_time(self, repo_ids: List[int], interval: str = "M") -> pd.DataFrame:
        """
        Get commit activity over time
        
        Args:
            repo_ids: List of repository IDs
            interval: Time interval (D, W, M, M3, M6, M12)
            
        Returns:
            DataFrame with commit activity over time
        """
        if not repo_ids:
            return pd.DataFrame()
            
        repo_ids_str = self.format_repo_ids_for_sql(repo_ids)
        
        # Map interval to PostgreSQL date_trunc format
        interval_map = {
            "D": "day",
            "W": "week", 
            "M": "month",
            "M3": "quarter",
            "M6": "month",  # Will need additional grouping
            "M12": "year"
        }
        
        trunc_interval = interval_map.get(interval, "month")
        
        query = f"""
            SELECT 
                date_trunc('{trunc_interval}', c.cmt_author_timestamp) as date,
                COUNT(DISTINCT c.cmt_commit_hash) as commit_count
            FROM commits c
            WHERE c.repo_id in ({repo_ids_str})
            GROUP BY date_trunc('{trunc_interval}', c.cmt_author_timestamp)
            ORDER BY date
        """
        
        df = self.execute_query(query)
        
        # Handle M6 (semi-annual) grouping
        if interval == "M6" and not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df['semester'] = df['date'].dt.to_period('6M')
            df = df.groupby('semester').agg({
                'commit_count': 'sum'
            }).reset_index()
            df['date'] = df['semester'].dt.start_time
            
        return df
    
    def get_top_authors(self, repo_ids: List[int], limit: int = 10) -> pd.DataFrame:
        """
        Get top authors by commit count
        
        Args:
            repo_ids: List of repository IDs
            limit: Number of top authors to return
            
        Returns:
            DataFrame with top authors
        """
        if not repo_ids:
            return pd.DataFrame()
            
        repo_ids_str = self.format_repo_ids_for_sql(repo_ids)
        
        query = f"""
            SELECT 
                c.cmt_author_name as author_name,
                c.cmt_author_email as author_email,
                COUNT(DISTINCT c.cmt_commit_hash) as commit_count,
                SUM(c.cmt_added) as total_lines_added,
                SUM(c.cmt_removed) as total_lines_removed,
                MIN(c.cmt_author_timestamp) as first_commit,
                MAX(c.cmt_author_timestamp) as last_commit
            FROM commits c
            WHERE c.repo_id in ({repo_ids_str})
            GROUP BY c.cmt_author_name, c.cmt_author_email
            ORDER BY commit_count DESC
            LIMIT {limit}
        """
        
        return self.execute_query(query)
    
    def get_commit_file_changes(self, repo_ids: List[int], limit: Optional[int] = None) -> pd.DataFrame:
        """
        Get commit file changes statistics
        
        Args:
            repo_ids: List of repository IDs
            limit: Maximum number of records to return
            
        Returns:
            DataFrame with file changes per commit
        """
        if not repo_ids:
            return pd.DataFrame()
            
        repo_ids_str = self.format_repo_ids_for_sql(repo_ids)
        limit_clause = f"LIMIT {limit}" if limit else ""
        
        query = f"""
            SELECT 
                c.cmt_commit_hash as commit_hash,
                c.cmt_author_timestamp as author_timestamp,
                COUNT(DISTINCT cf.file_path) as files_changed,
                SUM(cf.file_added) as total_lines_added,
                SUM(cf.file_removed) as total_lines_removed
            FROM commits c
            LEFT JOIN commit_files cf ON c.cmt_commit_hash = cf.cmt_commit_hash
            WHERE c.repo_id in ({repo_ids_str})
            GROUP BY c.cmt_commit_hash, c.cmt_author_timestamp
            ORDER BY c.cmt_author_timestamp DESC
            {limit_clause}
        """
        
        return self.execute_query(query)
    
    def get_avg_files_per_commit(self, repo_ids: List[int]) -> float:
        """
        Get average number of files changed per commit
        
        Args:
            repo_ids: List of repository IDs
            
        Returns:
            Average files per commit
        """
        if not repo_ids:
            return 0.0
            
        repo_ids_str = self.format_repo_ids_for_sql(repo_ids)
        
        query = f"""
            SELECT 
                AVG(file_count) as avg_files_per_commit
            FROM (
                SELECT 
                    c.cmt_commit_hash,
                    COUNT(DISTINCT cf.file_path) as file_count
                FROM commits c
                LEFT JOIN commit_files cf ON c.cmt_commit_hash = cf.cmt_commit_hash
                WHERE c.repo_id in ({repo_ids_str})
                GROUP BY c.cmt_commit_hash
            ) as commit_file_counts
        """
        
        df = self.execute_query(query)
        return float(df.iloc[0]['avg_files_per_commit']) if not df.empty else 0.0
    
    def get_commit_activity_by_day(self, repo_ids: List[int]) -> pd.DataFrame:
        """
        Get commit activity by day of week
        
        Args:
            repo_ids: List of repository IDs
            
        Returns:
            DataFrame with commit activity by day of week
        """
        if not repo_ids:
            return pd.DataFrame()
            
        repo_ids_str = self.format_repo_ids_for_sql(repo_ids)
        
        query = f"""
            SELECT 
                EXTRACT(DOW FROM c.cmt_author_timestamp) as day_of_week,
                CASE EXTRACT(DOW FROM c.cmt_author_timestamp)
                    WHEN 0 THEN 'Sunday'
                    WHEN 1 THEN 'Monday'
                    WHEN 2 THEN 'Tuesday'
                    WHEN 3 THEN 'Wednesday'
                    WHEN 4 THEN 'Thursday'
                    WHEN 5 THEN 'Friday'
                    WHEN 6 THEN 'Saturday'
                END as day_name,
                COUNT(DISTINCT c.cmt_commit_hash) as commit_count
            FROM commits c
            WHERE c.repo_id in ({repo_ids_str})
            GROUP BY EXTRACT(DOW FROM c.cmt_author_timestamp)
            ORDER BY day_of_week
        """
        
        return self.execute_query(query)
    
    def get_commit_activity_by_hour(self, repo_ids: List[int]) -> pd.DataFrame:
        """
        Get commit activity by hour of day
        
        Args:
            repo_ids: List of repository IDs
            
        Returns:
            DataFrame with commit activity by hour
        """
        if not repo_ids:
            return pd.DataFrame()
            
        repo_ids_str = self.format_repo_ids_for_sql(repo_ids)
        
        query = f"""
            SELECT 
                EXTRACT(HOUR FROM c.cmt_author_timestamp) as hour_of_day,
                COUNT(DISTINCT c.cmt_commit_hash) as commit_count
            FROM commits c
            WHERE c.repo_id in ({repo_ids_str})
            GROUP BY EXTRACT(HOUR FROM c.cmt_author_timestamp)
            ORDER BY hour_of_day
        """
        
        return self.execute_query(query)
    
    def get_repository_commit_summary(self, repo_ids: List[int]) -> pd.DataFrame:
        """
        Get commit summary by repository
        
        Args:
            repo_ids: List of repository IDs
            
        Returns:
            DataFrame with commit summary per repository
        """
        if not repo_ids:
            return pd.DataFrame()
            
        repo_ids_str = self.format_repo_ids_for_sql(repo_ids)
        
        query = f"""
            SELECT 
                r.repo_id,
                r.repo_name,
                COUNT(DISTINCT c.cmt_commit_hash) as commit_count,
                COUNT(DISTINCT c.cmt_author_email) as unique_authors,
                MIN(c.cmt_author_timestamp) as first_commit,
                MAX(c.cmt_author_timestamp) as last_commit,
                AVG(c.cmt_added) as avg_lines_added,
                AVG(c.cmt_removed) as avg_lines_removed
            FROM repo r
            LEFT JOIN commits c ON r.repo_id = c.repo_id
            WHERE r.repo_id in ({repo_ids_str})
            GROUP BY r.repo_id, r.repo_name
            ORDER BY commit_count DESC
        """
        
        return self.execute_query(query) 