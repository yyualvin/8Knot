"""
8Knot API Usage Examples
=======================

This script demonstrates how to use the 8Knot API to generate standalone
Plotly visualizations and calculate metrics.

Before running this script, make sure you have:
1. Database connection configured (environment variables)
2. Required dependencies installed
3. Valid repository IDs

Usage:
    python basic_usage.py
"""

import os
import sys
import logging
from typing import List

# Add the API to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from api.config import get_config
from api.queries.affiliation_query import AffiliationQuery
from api.queries.commits_query import CommitsQuery
from api.visualizations.affiliation_visualization import AffiliationVisualization
from api.metrics.commit_metrics import CommitMetrics
from api.utils import DataUtils

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main example function"""
    print("8Knot API Usage Examples")
    print("=" * 40)
    
    # Example repository IDs (replace with your actual repo IDs)
    repo_ids = [1, 2, 3]  # Replace with actual repository IDs
    
    # Test configuration
    print("\n1. Testing Configuration")
    config = get_config()
    if config.test_connection():
        print("✓ Database connection successful")
    else:
        print("✗ Database connection failed")
        return
    
    # Example 1: Simple query usage
    print("\n2. Simple Query Usage")
    try:
        affiliation_query = AffiliationQuery()
        org_data = affiliation_query.get_organization_activity(repo_ids, min_contributions=1)
        print(f"✓ Found {len(org_data)} organizations")
        if not org_data.empty:
            print(f"Top organization: {org_data.iloc[0]['domains']}")
    except Exception as e:
        print(f"✗ Query failed: {str(e)}")
    
    # Example 2: Visualization generation
    print("\n3. Visualization Generation")
    try:
        affiliation_viz = AffiliationVisualization()
        result = affiliation_viz.generate_organization_bar_chart(repo_ids, min_contributions=1)
        
        if result['success']:
            print("✓ Bar chart generated successfully")
            print(f"Data points: {result['data_points']}")
            print(f"Processing time: {result.get('processing_time_seconds', 0)}s")
            
            # Save chart to file (optional)
            # with open('organization_chart.json', 'w') as f:
            #     json.dump(result['data'], f, indent=2)
            
        else:
            print(f"✗ Visualization failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"✗ Visualization failed: {str(e)}")
    
    # Example 3: Multiple chart types
    print("\n4. Multiple Chart Types")
    try:
        affiliation_viz = AffiliationVisualization()
        
        # Bar chart
        bar_result = affiliation_viz.generate_organization_bar_chart(repo_ids)
        print(f"✓ Bar chart: {bar_result['success']}")
        
        # Pie chart
        pie_result = affiliation_viz.generate_organization_pie_chart(repo_ids)
        print(f"✓ Pie chart: {pie_result['success']}")
        
        # Table
        table_result = affiliation_viz.generate_organization_table(repo_ids)
        print(f"✓ Table: {table_result['success']}")
        
    except Exception as e:
        print(f"✗ Multiple charts failed: {str(e)}")
    
    # Example 4: Metrics calculation
    print("\n5. Metrics Calculation")
    try:
        commit_metrics = CommitMetrics()
        
        # Simple metric
        total_commits = commit_metrics.get_total_commits(repo_ids)
        print(f"✓ Total commits: {total_commits}")
        
        # Comprehensive metrics
        metrics_summary = commit_metrics.get_commit_metrics_summary(repo_ids)
        print(f"✓ Unique authors: {metrics_summary.get('unique_authors', 0)}")
        print(f"✓ Avg lines added: {metrics_summary.get('avg_lines_added', 0)}")
        
    except Exception as e:
        print(f"✗ Metrics calculation failed: {str(e)}")
    
    # Example 5: Direct data access
    print("\n6. Direct Data Access")
    try:
        commits_query = CommitsQuery()
        commits_data = commits_query.get_commits_over_time(repo_ids, interval="M")
        print(f"✓ Retrieved {len(commits_data)} time periods")
        
        if not commits_data.empty:
            print(f"Date range: {commits_data['date'].min()} to {commits_data['date'].max()}")
            
    except Exception as e:
        print(f"✗ Direct data access failed: {str(e)}")
    
    # Example 6: Error handling
    print("\n7. Error Handling")
    try:
        # Test with invalid repo IDs
        invalid_repo_ids = [-1, 0]
        affiliation_viz = AffiliationVisualization()
        result = affiliation_viz.generate_organization_bar_chart(invalid_repo_ids)
        print(f"✓ Error handling: {not result['success']}")
        
    except Exception as e:
        print(f"✗ Error handling test failed: {str(e)}")
    
    print("\n" + "=" * 40)
    print("Examples completed!")

def demonstrate_parameters():
    """Demonstrate parameter usage"""
    print("\nParameter Usage Examples")
    print("-" * 30)
    
    repo_ids = [1, 2, 3]  # Replace with actual repository IDs
    
    # Different parameters for affiliation queries
    affiliation_query = AffiliationQuery()
    
    # Minimum contributions filter
    org_data_min1 = affiliation_query.get_organization_activity(repo_ids, min_contributions=1)
    org_data_min5 = affiliation_query.get_organization_activity(repo_ids, min_contributions=5)
    
    print(f"Organizations with min 1 contribution: {len(org_data_min1)}")
    print(f"Organizations with min 5 contributions: {len(org_data_min5)}")
    
    # Email domain filtering
    domain_data_all = affiliation_query.get_email_domains(repo_ids, include_common=True)
    domain_data_filtered = affiliation_query.get_email_domains(repo_ids, include_common=False)
    
    print(f"All domains: {len(domain_data_all)}")
    print(f"Filtered domains: {len(domain_data_filtered)}")
    
    # Commit queries with different intervals
    commits_query = CommitsQuery()
    
    monthly_data = commits_query.get_commits_over_time(repo_ids, interval="M")
    quarterly_data = commits_query.get_commits_over_time(repo_ids, interval="M3")
    
    print(f"Monthly data points: {len(monthly_data)}")
    print(f"Quarterly data points: {len(quarterly_data)}")

def demonstrate_advanced_usage():
    """Demonstrate advanced usage patterns"""
    print("\nAdvanced Usage Examples")
    print("-" * 30)
    
    repo_ids = [1, 2, 3]  # Replace with actual repository IDs
    
    # Chaining operations
    affiliation_query = AffiliationQuery()
    
    # Get raw data
    raw_data = affiliation_query.get_organization_activity(repo_ids)
    
    # Process data
    processed_data = affiliation_query.process_affiliation_data(
        raw_data, 
        min_contributions=2,
        group_threshold=0.05
    )
    
    print(f"Raw data: {len(raw_data)} organizations")
    print(f"Processed data: {len(processed_data)} organizations")
    
    # Custom visualization with processed data
    affiliation_viz = AffiliationVisualization()
    
    # Create custom chart
    custom_chart = affiliation_viz.create_organization_bar_chart(
        processed_data,
        title="Custom Organization Chart",
        x_label="Email Domains",
        y_label="Number of Contributors"
    )
    
    print(f"Custom chart created: {custom_chart is not None}")

if __name__ == "__main__":
    # Run basic examples
    main()
    
    # Uncomment to run additional examples
    # demonstrate_parameters()
    # demonstrate_advanced_usage() 