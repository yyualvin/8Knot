"""
8Knot API Affiliation Query
==========================

Query functions for organization affiliation data including email domain analysis,
contributor company affiliations, and organization activity metrics.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import logging
from datetime import datetime

from ..base import BaseQuery
from ..utils import DataUtils, FormatUtils

logger = logging.getLogger(__name__)

class AffiliationQuery(BaseQuery):
    """Query engine for organization affiliation data"""
    
    def get_data(self, repo_ids: List[int], **kwargs) -> pd.DataFrame:
        """
        Get affiliation data for repositories
        
        Args:
            repo_ids: List of repository IDs
            **kwargs: Additional parameters
            
        Returns:
            DataFrame with affiliation data
        """
        return self.get_contributor_actions(repo_ids, **kwargs)
    
    def get_contributor_actions(self, repo_ids: List[int], limit: Optional[int] = None) -> pd.DataFrame:
        """
        Get contributor actions with organization affiliation data
        
        Args:
            repo_ids: List of repository IDs
            limit: Maximum number of records to return
            
        Returns:
            DataFrame with contributor actions and affiliations
        """
        if not repo_ids:
            return pd.DataFrame()
            
        repo_ids_str = self.format_repo_ids_for_sql(repo_ids)
        limit_clause = f"LIMIT {limit}" if limit else ""
        
        query = f"""
            SELECT
                left(c.cntrb_id::text, 15) as cntrb_id,
                timezone('utc', c.created_at) AS created_at,
                c.repo_id,
                c.login,
                c.action,
                c.rank,
                con.cntrb_company,
                string_agg(ca.alias_email, ' , ' order by ca.alias_email) as email_list
            FROM
                explorer_contributor_actions c
            JOIN contributors_aliases ca
                ON c.cntrb_id = ca.cntrb_id
            JOIN contributors con
                ON c.cntrb_id = con.cntrb_id
            WHERE
                c.repo_id in ({repo_ids_str})
                and timezone('utc', c.created_at) < now()
            GROUP BY c.cntrb_id, c.created_at, c.repo_id, c.login, c.action, c.rank, con.cntrb_company
            ORDER BY
                c.created_at
            {limit_clause}
        """
        
        return self.execute_query(query)
    
    def get_organization_activity(self, repo_ids: List[int], min_contributions: int = 1) -> pd.DataFrame:
        """
        Get organization activity by email domain
        
        Args:
            repo_ids: List of repository IDs
            min_contributions: Minimum contributions to include organization
            
        Returns:
            DataFrame with organization activity data
        """
        if not repo_ids:
            return pd.DataFrame()
            
        repo_ids_str = self.format_repo_ids_for_sql(repo_ids)
        
        query = f"""
            SELECT 
                CASE 
                    WHEN position('@' in ca.alias_email) > 0 
                    THEN substring(ca.alias_email from position('@' in ca.alias_email) + 1)
                    ELSE 'Unknown'
                END as domains,
                COUNT(DISTINCT c.cntrb_id) as occurrences
            FROM 
                explorer_contributor_actions c
            JOIN contributors_aliases ca 
                ON c.cntrb_id = ca.cntrb_id
            WHERE 
                c.repo_id in ({repo_ids_str})
                AND ca.alias_email IS NOT NULL
                AND ca.alias_email != ''
                AND position('@' in ca.alias_email) > 0
            GROUP BY domains
            HAVING COUNT(DISTINCT c.cntrb_id) >= {min_contributions}
            ORDER BY occurrences DESC
        """
        
        return self.execute_query(query)
    
    def get_company_affiliations(self, repo_ids: List[int]) -> pd.DataFrame:
        """
        Get company affiliations for contributors
        
        Args:
            repo_ids: List of repository IDs
            
        Returns:
            DataFrame with company affiliation data
        """
        if not repo_ids:
            return pd.DataFrame()
            
        repo_ids_str = self.format_repo_ids_for_sql(repo_ids)
        
        query = f"""
            SELECT 
                con.cntrb_company,
                COUNT(DISTINCT c.cntrb_id) as contributor_count,
                COUNT(c.cntrb_id) as total_contributions
            FROM 
                explorer_contributor_actions c
            JOIN contributors con 
                ON c.cntrb_id = con.cntrb_id
            WHERE 
                c.repo_id in ({repo_ids_str})
                AND con.cntrb_company IS NOT NULL
                AND con.cntrb_company != ''
            GROUP BY con.cntrb_company
            ORDER BY total_contributions DESC
        """
        
        return self.execute_query(query)
    
    def get_email_domains(self, repo_ids: List[int], include_common: bool = True) -> pd.DataFrame:
        """
        Get email domains and their activity
        
        Args:
            repo_ids: List of repository IDs
            include_common: Whether to include common domains (gmail, etc.)
            
        Returns:
            DataFrame with email domain data
        """
        if not repo_ids:
            return pd.DataFrame()
            
        repo_ids_str = self.format_repo_ids_for_sql(repo_ids)
        
        # Common email domains to potentially exclude
        common_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'protonmail.com']
        exclude_clause = ""
        if not include_common:
            domain_list = "', '".join(common_domains)
            exclude_clause = f"AND domains NOT IN ('{domain_list}')"
        
        query = f"""
            SELECT 
                CASE 
                    WHEN position('@' in ca.alias_email) > 0 
                    THEN substring(ca.alias_email from position('@' in ca.alias_email) + 1)
                    ELSE 'Unknown'
                END as domains,
                COUNT(DISTINCT c.cntrb_id) as unique_contributors,
                COUNT(c.cntrb_id) as total_contributions,
                MIN(c.created_at) as first_contribution,
                MAX(c.created_at) as last_contribution
            FROM 
                explorer_contributor_actions c
            JOIN contributors_aliases ca 
                ON c.cntrb_id = ca.cntrb_id
            WHERE 
                c.repo_id in ({repo_ids_str})
                AND ca.alias_email IS NOT NULL
                AND ca.alias_email != ''
                AND position('@' in ca.alias_email) > 0
            GROUP BY domains
            {exclude_clause}
            ORDER BY total_contributions DESC
        """
        
        return self.execute_query(query)
    
    def get_contributor_details(self, repo_ids: List[int], cntrb_id: Optional[str] = None) -> pd.DataFrame:
        """
        Get detailed contributor information
        
        Args:
            repo_ids: List of repository IDs
            cntrb_id: Specific contributor ID (optional)
            
        Returns:
            DataFrame with contributor details
        """
        if not repo_ids:
            return pd.DataFrame()
            
        repo_ids_str = self.format_repo_ids_for_sql(repo_ids)
        cntrb_filter = f"AND c.cntrb_id = '{cntrb_id}'" if cntrb_id else ""
        
        query = f"""
            SELECT 
                c.cntrb_id,
                c.login,
                con.cntrb_company,
                STRING_AGG(DISTINCT ca.alias_email, ', ') as email_list,
                COUNT(DISTINCT c.repo_id) as repo_count,
                COUNT(c.action) as total_actions,
                COUNT(CASE WHEN c.action = 'commit' THEN 1 END) as commits,
                COUNT(CASE WHEN c.action = 'issue' THEN 1 END) as issues,
                COUNT(CASE WHEN c.action = 'pull_request' THEN 1 END) as pull_requests,
                MIN(c.created_at) as first_activity,
                MAX(c.created_at) as last_activity
            FROM 
                explorer_contributor_actions c
            JOIN contributors con 
                ON c.cntrb_id = con.cntrb_id
            LEFT JOIN contributors_aliases ca 
                ON c.cntrb_id = ca.cntrb_id
            WHERE 
                c.repo_id in ({repo_ids_str})
                {cntrb_filter}
            GROUP BY c.cntrb_id, c.login, con.cntrb_company
            ORDER BY total_actions DESC
        """
        
        return self.execute_query(query)
    
    def get_affiliation_summary(self, repo_ids: List[int]) -> Dict[str, Any]:
        """
        Get summary of affiliation data
        
        Args:
            repo_ids: List of repository IDs
            
        Returns:
            Dictionary with affiliation summary
        """
        if not repo_ids:
            return {}
        
        # Get basic counts
        org_df = self.get_organization_activity(repo_ids)
        company_df = self.get_company_affiliations(repo_ids)
        domain_df = self.get_email_domains(repo_ids)
        
        return {
            "total_organizations": len(org_df),
            "total_companies": len(company_df),
            "total_email_domains": len(domain_df),
            "top_organization": org_df.iloc[0]['domains'] if not org_df.empty else None,
            "top_company": company_df.iloc[0]['cntrb_company'] if not company_df.empty else None,
            "most_active_domain": domain_df.iloc[0]['domains'] if not domain_df.empty else None,
            "repository_count": len(repo_ids)
        }
    
    def process_affiliation_data(self, df: pd.DataFrame, min_contributions: int = 1, 
                                group_threshold: float = 0.01) -> pd.DataFrame:
        """
        Process affiliation data for visualization
        
        Args:
            df: Raw affiliation data
            min_contributions: Minimum contributions to include
            group_threshold: Threshold for grouping small values
            
        Returns:
            Processed DataFrame
        """
        if df.empty:
            return df
            
        # Filter by minimum contributions
        df_filtered = df[df['occurrences'] >= min_contributions].copy()
        
        # Group small values using utility function
        df_processed = DataUtils.group_small_values(
            df_filtered, 
            value_col='occurrences', 
            label_col='domains', 
            threshold=group_threshold
        )
        
        # Sort by occurrences
        df_processed = df_processed.sort_values('occurrences', ascending=False)
        
        return df_processed 