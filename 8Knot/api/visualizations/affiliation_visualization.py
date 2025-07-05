"""
8Knot API Affiliation Visualization
==================================

Visualization generators for organization affiliation data including bar charts,
pie charts, and tables for email domain analysis and company affiliations.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import logging

from ..base import BaseVisualization, BaseTable, BaseChart
from ..queries.affiliation_query import AffiliationQuery
from ..utils import DataUtils

logger = logging.getLogger(__name__)

class AffiliationVisualization(BaseChart, BaseTable):
    """Visualization generator for organization affiliation data"""
    
    def __init__(self, query_engine: Optional[AffiliationQuery] = None):
        """
        Initialize affiliation visualization generator
        
        Args:
            query_engine: AffiliationQuery instance
        """
        super().__init__(query_engine or AffiliationQuery())
    
    def create_figure(self, df: pd.DataFrame, **kwargs) -> go.Figure:
        """
        Create default affiliation figure (bar chart)
        
        Args:
            df: DataFrame with affiliation data
            **kwargs: Additional parameters
            
        Returns:
            Plotly figure
        """
        return self.create_organization_bar_chart(df, **kwargs)
    
    def create_organization_bar_chart(self, df: pd.DataFrame, 
                                    title: str = "Organization Activity by Email Domain",
                                    x_label: str = "Email Domains",
                                    y_label: str = "Contributions") -> go.Figure:
        """
        Create bar chart for organization activity
        
        Args:
            df: DataFrame with domains and occurrences columns
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            
        Returns:
            Plotly bar chart figure
        """
        if df.empty:
            return self.create_no_data_figure(title)
        
        # Ensure we have the required columns
        if 'domains' not in df.columns or 'occurrences' not in df.columns:
            return self.create_error_figure(title, "Missing required columns: domains, occurrences")
        
        fig = px.bar(
            df,
            x="domains",
            y="occurrences",
            title=title,
            labels={"domains": x_label, "occurrences": y_label},
            color_discrete_sequence=self.color_sequence
        )
        
        fig.update_layout(
            xaxis_title=x_label,
            yaxis_title=y_label,
            bargroupgap=0.1,
            showlegend=False
        )
        
        # Rotate x-axis labels if there are many domains
        if len(df) > 10:
            fig.update_layout(xaxis_tickangle=-45)
        
        return self.apply_template(fig)
    
    def create_organization_pie_chart(self, df: pd.DataFrame,
                                    title: str = "Organization Distribution by Email Domain") -> go.Figure:
        """
        Create pie chart for organization distribution
        
        Args:
            df: DataFrame with domains and occurrences columns
            title: Chart title
            
        Returns:
            Plotly pie chart figure
        """
        if df.empty:
            return self.create_no_data_figure(title)
        
        if 'domains' not in df.columns or 'occurrences' not in df.columns:
            return self.create_error_figure(title, "Missing required columns: domains, occurrences")
        
        fig = px.pie(
            df,
            values="occurrences",
            names="domains",
            title=title,
            color_discrete_sequence=self.color_sequence
        )
        
        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="%{label}<br>Contributions: %{value}<br>Percentage: %{percent}<extra></extra>"
        )
        
        return self.apply_template(fig)
    
    def create_organization_table(self, df: pd.DataFrame,
                                title: str = "Organization Activity by Email Domain") -> go.Figure:
        """
        Create table for organization data
        
        Args:
            df: DataFrame with domains and occurrences columns
            title: Table title
            
        Returns:
            Plotly table figure
        """
        if df.empty:
            return self.create_no_data_figure(title)
        
        if 'domains' not in df.columns or 'occurrences' not in df.columns:
            return self.create_error_figure(title, "Missing required columns: domains, occurrences")
        
        # Format the data for display
        display_df = df.copy()
        display_df['domains'] = display_df['domains'].str.strip()
        display_df = display_df.sort_values('occurrences', ascending=False)
        
        return self.create_table_figure(
            display_df,
            columns=["Organization (Email Domain)", "Contributions"],
            title=title
        )
    
    def create_company_bar_chart(self, df: pd.DataFrame,
                               title: str = "Company Affiliations",
                               limit: int = 20) -> go.Figure:
        """
        Create bar chart for company affiliations
        
        Args:
            df: DataFrame with company affiliation data
            title: Chart title
            limit: Maximum number of companies to show
            
        Returns:
            Plotly bar chart figure
        """
        if df.empty:
            return self.create_no_data_figure(title)
        
        # Limit the number of companies displayed
        df_limited = df.head(limit)
        
        fig = px.bar(
            df_limited,
            x="cntrb_company",
            y="total_contributions",
            title=title,
            labels={"cntrb_company": "Company", "total_contributions": "Total Contributions"},
            color_discrete_sequence=self.color_sequence
        )
        
        fig.update_layout(
            xaxis_title="Company",
            yaxis_title="Total Contributions",
            bargroupgap=0.1,
            showlegend=False
        )
        
        # Rotate x-axis labels for better readability
        fig.update_layout(xaxis_tickangle=-45)
        
        return self.apply_template(fig)
    
    def create_email_domain_treemap(self, df: pd.DataFrame,
                                  title: str = "Email Domain Distribution") -> go.Figure:
        """
        Create treemap for email domain distribution
        
        Args:
            df: DataFrame with domains and occurrences columns
            title: Chart title
            
        Returns:
            Plotly treemap figure
        """
        if df.empty:
            return self.create_no_data_figure(title)
        
        if 'domains' not in df.columns or 'occurrences' not in df.columns:
            return self.create_error_figure(title, "Missing required columns: domains, occurrences")
        
        fig = px.treemap(
            df,
            path=['domains'],
            values='occurrences',
            title=title,
            color_discrete_sequence=self.color_sequence
        )
        
        fig.update_traces(
            texttemplate="<b>%{label}</b><br>%{value} contributions",
            hovertemplate="%{label}<br>Contributions: %{value}<extra></extra>"
        )
        
        return self.apply_template(fig)
    
    def create_contributor_activity_timeline(self, df: pd.DataFrame,
                                          title: str = "Contributor Activity Timeline") -> go.Figure:
        """
        Create timeline chart for contributor activity
        
        Args:
            df: DataFrame with contributor actions data
            title: Chart title
            
        Returns:
            Plotly timeline figure
        """
        if df.empty:
            return self.create_no_data_figure(title)
        
        # Group by date and count activities
        if 'created_at' not in df.columns:
            return self.create_error_figure(title, "Missing required column: created_at")
        
        df['date'] = pd.to_datetime(df['created_at']).dt.date
        timeline_df = df.groupby('date').size().reset_index(name='activity_count')
        
        fig = px.line(
            timeline_df,
            x='date',
            y='activity_count',
            title=title,
            labels={'date': 'Date', 'activity_count': 'Activity Count'},
            color_discrete_sequence=self.color_sequence
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Activity Count",
            showlegend=False
        )
        
        return self.apply_template(fig)
    
    # High-level methods that combine queries and visualizations
    def generate_organization_bar_chart(self, repo_ids: List[int], min_contributions: int = 1,
                                      **kwargs) -> Dict[str, Any]:
        """
        Generate organization bar chart with data fetching
        
        Args:
            repo_ids: List of repository IDs
            min_contributions: Minimum contributions to include
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with chart JSON and metadata
        """
        try:
            # Get data
            df = self.query_engine.get_organization_activity(repo_ids, min_contributions)
            
            # Process data for visualization
            df_processed = self.query_engine.process_affiliation_data(df, min_contributions)
            
            # Create chart
            fig = self.create_organization_bar_chart(df_processed, **kwargs)
            
            return {
                "success": True,
                "data": fig.to_dict(),
                "message": f"Organization bar chart generated for {len(repo_ids)} repositories",
                "repo_count": len(repo_ids),
                "data_points": len(df_processed)
            }
            
        except Exception as e:
            logger.error(f"Error generating organization bar chart: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": self.create_error_figure().to_dict()
            }
    
    def generate_organization_pie_chart(self, repo_ids: List[int], min_contributions: int = 1,
                                      **kwargs) -> Dict[str, Any]:
        """
        Generate organization pie chart with data fetching
        
        Args:
            repo_ids: List of repository IDs
            min_contributions: Minimum contributions to include
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with chart JSON and metadata
        """
        try:
            # Get data
            df = self.query_engine.get_organization_activity(repo_ids, min_contributions)
            
            # Process data for visualization
            df_processed = self.query_engine.process_affiliation_data(df, min_contributions)
            
            # Create chart
            fig = self.create_organization_pie_chart(df_processed, **kwargs)
            
            return {
                "success": True,
                "data": fig.to_dict(),
                "message": f"Organization pie chart generated for {len(repo_ids)} repositories",
                "repo_count": len(repo_ids),
                "data_points": len(df_processed)
            }
            
        except Exception as e:
            logger.error(f"Error generating organization pie chart: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": self.create_error_figure().to_dict()
            }
    
    def generate_organization_table(self, repo_ids: List[int], min_contributions: int = 1,
                                  **kwargs) -> Dict[str, Any]:
        """
        Generate organization table with data fetching
        
        Args:
            repo_ids: List of repository IDs
            min_contributions: Minimum contributions to include
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with table JSON and metadata
        """
        try:
            # Get data
            df = self.query_engine.get_organization_activity(repo_ids, min_contributions)
            
            # Process data for visualization
            df_processed = self.query_engine.process_affiliation_data(df, min_contributions)
            
            # Create table
            fig = self.create_organization_table(df_processed, **kwargs)
            
            return {
                "success": True,
                "data": fig.to_dict(),
                "message": f"Organization table generated for {len(repo_ids)} repositories",
                "repo_count": len(repo_ids),
                "data_points": len(df_processed)
            }
            
        except Exception as e:
            logger.error(f"Error generating organization table: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": self.create_error_figure().to_dict()
            } 