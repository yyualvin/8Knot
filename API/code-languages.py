#!/usr/bin/env python3
"""
Standalone Repository Languages Analysis Example
===============================================

This script demonstrates how to:
1. Connect to an Augur database
2. Query repository language data
3. Process and analyze the data
4. Create a Plotly pie chart visualization

Based on the 8Knot repo_languages functionality.
"""

import os
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv("env.list")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Custom color sequence (from 8Knot)
COLOR_SEQUENCE = [
    "#B5B682",  # sage
    "#c0bc5d",  # citron (yellow-ish)
    "#6C8975",  # reseda green
    "#D9AE8E",  # buff (pale pink)
    "#FFBF51",  # xanthous (orange-ish)
    "#C7A5A5",  # rosy brown
]

# # Configure Plotly template
# pio.templates["custom_dark"] = pio.templates["slate"]
# pio.templates["custom_dark"]["layout"]["colorway"] = COLOR_SEQUENCE
# pio.templates.default = "custom_dark"


class AugurConnection:
    """Simple Augur database connection manager"""
    
    def __init__(self):
        """Initialize connection using environment variables"""
        self.engine = None
        self._load_credentials()
        
    def _load_credentials(self):
        """Load database credentials from environment variables"""
        required_vars = ["AUGUR_USERNAME", "AUGUR_PASSWORD", "AUGUR_HOST", 
                        "AUGUR_PORT", "AUGUR_DATABASE", "AUGUR_SCHEMA"]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            print("\nPlease set the following environment variables:")
            for var in missing_vars:
                print(f"  export {var}=your_value")
            sys.exit(1)
        
        self.user = os.getenv("AUGUR_USERNAME")
        self.password = os.getenv("AUGUR_PASSWORD")
        self.host = os.getenv("AUGUR_HOST")
        self.port = os.getenv("AUGUR_PORT")
        self.database = os.getenv("AUGUR_DATABASE")
        self.schema = os.getenv("AUGUR_SCHEMA")
        
    def connect(self):
        """Create and test database connection"""
        try:
            connection_string = f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
            
            self.engine = sa.create_engine(
                connection_string,
                connect_args={"options": f"-csearch_path={self.schema}"},
                pool_pre_ping=True
            )
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(sa.text("SELECT 1"))
                
            logger.info("✅ Database connection successful")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
            
    def query_repo_languages(self, repo_ids: List[int]) -> Optional[pd.DataFrame]:
        """
        Query repository language data from Augur database
        
        Args:
            repo_ids: List of repository IDs to query
            
        Returns:
            DataFrame with columns: id, programming_language, code_lines, files
        """
        if not self.engine:
            logger.error("Database not connected")
            return None
            
        if not repo_ids:
            logger.warning("No repository IDs provided")
            return None
            
        # The original query from 8Knot
        query = """
        SELECT
            repo_id as id,
            programming_language,
            code_lines,
            files
        FROM explorer_repo_languages
        WHERE repo_id = ANY(:repo_ids)
        """
        
        try:
            logger.info(f"Querying language data for {len(repo_ids)} repositories")
            df = pd.read_sql(
                sa.text(query), 
                con=self.engine, 
                params={"repo_ids": repo_ids}
            )
            
            if df.empty:
                logger.warning("No language data found for the specified repositories")
                return None
                
            logger.info(f"Retrieved {len(df)} language records")
            return df
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return None
            
    def get_available_repos(self, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Get available repositories with language data
        
        Args:
            limit: Number of repositories to return (None for all)
            
        Returns:
            DataFrame with repo information
        """
        if not self.engine:
            logger.error("Database not connected")
            return pd.DataFrame()
            
        # Base query without limit
        base_query = """
        SELECT 
            r.repo_id,
            r.repo_name,
            r.repo_git,
            rg.rg_name as organization
        FROM repo r
        JOIN repo_groups rg ON r.repo_group_id = rg.repo_group_id
        WHERE r.repo_id IN (
            SELECT DISTINCT repo_id 
            FROM explorer_repo_languages 
            ORDER BY repo_id
        )
        ORDER BY r.repo_name
        """
        
        # Add limit if specified
        if limit is not None:
            query = base_query.replace("ORDER BY r.repo_name", f"ORDER BY r.repo_name LIMIT {limit}")
            params = {}
        else:
            query = base_query
            params = {}
        
        try:
            df = pd.read_sql(
                sa.text(query),
                con=self.engine,
                params=params
            )
            return df
        except Exception as e:
            logger.error(f"Failed to get available repos: {e}")
            return pd.DataFrame()
            
    def get_repo_stats(self) -> dict:
        """
        Get statistics about available repositories
        
        Returns:
            Dictionary with repository statistics
        """
        if not self.engine:
            logger.error("Database not connected")
            return {}
            
        query = """
        SELECT 
            COUNT(DISTINCT r.repo_id) as total_repos,
            COUNT(DISTINCT rg.rg_name) as total_organizations,
            COUNT(DISTINCT erl.programming_language) as total_languages
        FROM repo r
        JOIN repo_groups rg ON r.repo_group_id = rg.repo_group_id
        JOIN explorer_repo_languages erl ON r.repo_id = erl.repo_id
        """
        
        try:
            result = pd.read_sql(sa.text(query), con=self.engine)
            return result.iloc[0].to_dict()
        except Exception as e:
            logger.error(f"Failed to get repo stats: {e}")
            return {}


def process_language_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process language data following 8Knot's approach
    
    Args:
        df: Raw language data from database
        
    Returns:
        Processed DataFrame ready for visualization
    """
    logger.info("Processing language data")
    
    # Copy to avoid modifying original
    df_processed = df.copy()
    
    # SVG files give one line of code per file (8Knot specific logic)
    df_processed.loc[df_processed["programming_language"] == "SVG", "code_lines"] = df_processed["files"]
    
    # Group by programming language and sum code lines and files
    df_lang = df_processed[["programming_language", "code_lines", "files"]].groupby("programming_language").sum().reset_index()
    
    # Require a language to have at least 0.1% of total files to be shown individually
    # Otherwise group into "Other"
    min_files = df_lang["files"].sum() / 1000
    df_lang.loc[df_lang["files"] <= min_files, "programming_language"] = "Other"
    
    # Re-group after "Other" assignment
    df_lang = df_lang[["programming_language", "code_lines", "files"]].groupby("programming_language").sum().reset_index()
    
    # Sort by file count (descending) and reset index
    df_lang = df_lang.sort_values(by="files", ascending=False).reset_index(drop=True)
    
    # Calculate percentages
    df_lang["code_percentage"] = (df_lang["code_lines"] / df_lang["code_lines"].sum()) * 100
    df_lang["files_percentage"] = (df_lang["files"] / df_lang["files"].sum()) * 100
    
    logger.info(f"Processed {len(df_lang)} language categories")
    return df_lang


def create_language_pie_chart(df: pd.DataFrame, view_mode: str = "files") -> go.Figure:
    """
    Create a pie chart visualization of programming languages
    
    Args:
        df: Processed language data
        view_mode: Either "files" or "lines" to determine what to visualize
        
    Returns:
        Plotly figure
    """
    logger.info(f"Creating pie chart (view mode: {view_mode})")
    
    # Determine which column to use for values
    if view_mode == "lines":
        values_col = "code_lines"
        title = "Programming Languages by Lines of Code"
    else:
        values_col = "files"
        title = "Programming Languages by Number of Files"
    
    # Create pie chart
    fig = px.pie(
        df,
        names="programming_language",
        values=values_col,
        title=title,
        color_discrete_sequence=COLOR_SEQUENCE
    )
    
    # Update traces for better display
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>" +
                     "Count: %{value}<br>" +
                     "Percentage: %{percent}<br>" +
                     "<extra></extra>"
    )
    
    # Update layout
    fig.update_layout(
        legend_title_text="Programming Languages",
        font=dict(size=12),
        width=800,
        height=600
    )
    
    return fig


def print_summary(df_raw: pd.DataFrame, df_processed: pd.DataFrame):
    """Print a summary of the language analysis"""
    print("\n" + "="*50)
    print("REPOSITORY LANGUAGE ANALYSIS SUMMARY")
    print("="*50)
    
    print(f"Total repositories analyzed: {df_raw['id'].nunique()}")
    print(f"Total language records: {len(df_raw)}")
    print(f"Unique languages found: {df_raw['programming_language'].nunique()}")
    print(f"Languages after processing: {len(df_processed)}")
    
    print(f"\nTotal files: {df_processed['files'].sum():,}")
    print(f"Total lines of code: {df_processed['code_lines'].sum():,}")
    
    print(f"\nTop 5 languages by files:")
    top_5 = df_processed.head(5)
    for _, row in top_5.iterrows():
        print(f"  {row['programming_language']}: {row['files']:,} files ({row['files_percentage']:.1f}%)")


def main():
    """Main function to demonstrate repo languages analysis"""
    print("Repository Languages Analysis - Standalone Example")
    print("Based on 8Knot functionality\n")
    
    # Initialize database connection
    db = AugurConnection()
    if not db.connect():
        sys.exit(1)
    
    # Show database statistics
    print("Database Statistics:")
    stats = db.get_repo_stats()
    if stats:
        print(f"  Total repositories: {stats.get('total_repos', 0)}")
        print(f"  Total organizations: {stats.get('total_organizations', 0)}")
        print(f"  Total programming languages: {stats.get('total_languages', 0)}")
    
    # Show available repositories
    print("\nAvailable repositories:")
    repos_df = db.get_available_repos()  # Get ALL repositories
    if repos_df.empty:
        print("No repositories found with language data")
        sys.exit(1)
    
    print(f"Found {len(repos_df)} repositories with language data")
    print(repos_df[['repo_id', 'repo_name', 'organization']].to_string(index=False))
    
    # Get user input for repository selection
    print(f"\nEnter repository IDs to analyze (comma-separated):")
    print(f"Example: {','.join(map(str, repos_df['repo_id'].head(3).tolist()))}")
    
    try:
        user_input = input("Repository IDs: ").strip()
        if not user_input:
            # Use first 3 repos as default
            repo_ids = repos_df['repo_id'].head(3).tolist()
            print(f"Using default repositories: {repo_ids}")
        else:
            repo_ids = [int(x.strip()) for x in user_input.split(',')]
    except (ValueError, KeyboardInterrupt):
        print("Invalid input or interrupted. Using default repositories.")
        repo_ids = repos_df['repo_id'].head(3).tolist()
    
    # Query language data
    df_raw = db.query_repo_languages(repo_ids)
    if df_raw is None:
        print("No language data found for the specified repositories")
        sys.exit(1)
    
    # Process the data
    df_processed = process_language_data(df_raw)
    
    # Print summary
    print_summary(df_raw, df_processed)
    
    # Create visualizations
    print("\nCreating visualizations...")
    
    # Create both file and line views
    fig_files = create_language_pie_chart(df_processed, "files")
    fig_lines = create_language_pie_chart(df_processed, "lines")
    
    # Display the charts
    print("\n📊 Displaying charts...")
    print("   - Files view: Shows distribution by number of files")
    print("   - Lines view: Shows distribution by lines of code")
    
    # Show the plots (this will open in browser)
    fig_files.show()
    fig_lines.show()
    
    # Optionally save as HTML
    save_html = input("\nSave charts as HTML files? (y/n): ").lower().strip()
    if save_html == 'y':
        fig_files.write_html("repo_languages_by_files.html")
        fig_lines.write_html("repo_languages_by_lines.html")
        print("✅ Charts saved as HTML files")
    
    print("\n🎉 Analysis complete!")


if __name__ == "__main__":
    main() 