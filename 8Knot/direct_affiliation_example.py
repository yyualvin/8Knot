"""
Direct Affiliation Query Example - Bypasses Cache Facade

This shows how to generate a Plotly table directly without using:
- Celery background tasks
- PostgreSQL cache facade
- Waiting/polling for data availability

Instead, it directly queries the database and returns Plotly JSON.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy import create_engine
import os
import logging
from typing import List, Dict, Any
import time


class DirectAffiliationQuery:
    """Direct database query approach without cache facade"""
    
    def __init__(self):
        # Direct database connection (same as AugurManager)
        self.engine = create_engine(
            f"postgresql://{os.getenv('AUGUR_DB_USER')}:"
            f"{os.getenv('AUGUR_DB_PASS')}@"
            f"{os.getenv('AUGUR_DB_HOST')}:"
            f"{os.getenv('AUGUR_DB_PORT')}/"
            f"{os.getenv('AUGUR_DB_NAME')}"
        )
    
    def get_affiliation_data(self, repo_ids: List[int]) -> pd.DataFrame:
        """
        Execute affiliation query directly and return DataFrame
        
        Args:
            repo_ids: List of repository IDs to query
            
        Returns:
            pandas DataFrame with affiliation data
        """
        logging.info(f"Executing direct affiliation query for {len(repo_ids)} repos")
        start_time = time.time()
        
        # Same query as in affiliation_query.py
        query = """
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
                c.repo_id = ANY(%(repo_ids)s)
                and timezone('utc', c.created_at) < now()
            GROUP BY c.cntrb_id, c.created_at, c.repo_id, c.login, c.action, c.rank, con.cntrb_company
            ORDER BY c.created_at
        """
        
        # Execute query directly
        df = pd.read_sql_query(query, self.engine, params={'repo_ids': repo_ids})
        
        logging.info(f"Direct query completed in {time.time() - start_time:.2f}s, got {len(df)} rows")
        return df
    
    def create_org_activity_table(self, repo_ids: List[int], min_contributions: int = 1) -> Dict[str, Any]:
        """
        Create Plotly table directly from database query
        
        Args:
            repo_ids: Repository IDs to analyze
            min_contributions: Minimum contributions to show organization
            
        Returns:
            Plotly figure as JSON-serializable dict
        """
        # Get data directly from database
        df = self.get_affiliation_data(repo_ids)
        
        if df.empty:
            return self._create_no_data_table()
        
        # Process data (same logic as current visualization)
        df = self._process_affiliation_data(df, min_contributions)
        
        # Create Plotly table
        fig = self._create_plotly_table(df)
        
        return fig.to_dict()
    
    def create_org_activity_chart(self, repo_ids: List[int], min_contributions: int = 1) -> Dict[str, Any]:
        """
        Create Plotly bar chart directly from database query
        
        Args:
            repo_ids: Repository IDs to analyze
            min_contributions: Minimum contributions to show organization
            
        Returns:
            Plotly figure as JSON-serializable dict
        """
        # Get data directly from database
        df = self.get_affiliation_data(repo_ids)
        
        if df.empty:
            return self._create_no_data_chart()
        
        # Process data (same logic as current visualization)
        df = self._process_affiliation_data(df, min_contributions)
        
        # Create Plotly bar chart
        fig = px.bar(
            df, 
            x="domains", 
            y="occurrences",
            title="Organization Activity by Email Domain",
            labels={"domains": "Email Domains", "occurrences": "Contributions"}
        )
        
        fig.update_layout(
            xaxis_title="Domains",
            yaxis_title="Contributions",
            bargroupgap=0.1,
            margin_b=40,
            font=dict(size=14),
        )
        
        return fig.to_dict()
    
    def _process_affiliation_data(self, df: pd.DataFrame, min_contributions: int) -> pd.DataFrame:
        """Process affiliation data (same logic as current visualization)"""
        # Convert to datetime
        df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
        
        # Sort chronologically
        df = df.sort_values(by="created_at", axis=0, ascending=True)
        
        # Extract email domains
        emails = df.email_list.str.split(" , ").explode("email_list").tolist()
        emails = [x.lower() for x in emails if "@" in x]
        email_domains = [x[x.rindex("@") + 1 :] for x in emails]
        
        # Count domain occurrences
        df_domains = pd.DataFrame(email_domains, columns=["domains"]).value_counts().to_frame().reset_index()
        df_domains = df_domains.rename(columns={"count": "occurrences"})
        
        # Group low-count domains as "Other"
        df_domains.loc[df_domains.occurrences <= min_contributions, "domains"] = "Other"
        df_domains = (
            df_domains.groupby(by="domains")["occurrences"]
            .sum()
            .reset_index()
            .sort_values(by=["occurrences"], ascending=False)
            .reset_index(drop=True)
        )
        
        # Remove "Other" category
        df_domains = df_domains[df_domains.domains != "Other"]
        
        return df_domains
    
    def _create_plotly_table(self, df: pd.DataFrame) -> go.Figure:
        """Create Plotly table from processed data"""
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=["Organization (Email Domain)", "Contributions"],
                fill_color='paleturquoise',
                align='left',
                font=dict(size=12, color='black')
            ),
            cells=dict(
                values=[df.domains, df.occurrences],
                fill_color='lightcyan',
                align='left',
                font=dict(size=11, color='black')
            )
        )])
        
        fig.update_layout(
            title="Organization Activity by Email Domain",
            height=400,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        return fig
    
    def _create_no_data_table(self) -> Dict[str, Any]:
        """Create empty table for no data case"""
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=["No Data Available"],
                fill_color='lightgray',
                align='center'
            ),
            cells=dict(
                values=[["No affiliation data found for selected repositories"]],
                fill_color='white',
                align='center'
            )
        )])
        fig.update_layout(title="Organization Activity", height=200)
        return fig.to_dict()
    
    def _create_no_data_chart(self) -> Dict[str, Any]:
        """Create empty chart for no data case"""
        fig = go.Figure()
        fig.update_layout(
            title="Organization Activity by Email Domain",
            annotations=[{
                'text': 'No affiliation data found for selected repositories',
                'showarrow': False,
                'x': 0.5,
                'y': 0.5,
                'xref': 'paper',
                'yref': 'paper',
                'font': {'size': 16}
            }]
        )
        return fig.to_dict()


# Example usage
if __name__ == "__main__":
    # Example: Direct query without cache facade
    query_engine = DirectAffiliationQuery()
    
    # Get sample repo IDs (you'd get these from your repo selection logic)
    repo_ids = [1, 2, 3]  # Example repo IDs
    
    # Get Plotly table directly - no caching, no waiting
    table_json = query_engine.create_org_activity_table(repo_ids, min_contributions=2)
    print("Table created directly:", len(str(table_json)), "characters")
    
    # Get Plotly chart directly - no caching, no waiting
    chart_json = query_engine.create_org_activity_chart(repo_ids, min_contributions=2)
    print("Chart created directly:", len(str(chart_json)), "characters") 