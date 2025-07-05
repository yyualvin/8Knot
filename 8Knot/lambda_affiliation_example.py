"""
AWS Lambda Function Example - Replacing Celery with Serverless

This shows how to convert 8Knot's Celery tasks to AWS Lambda functions
for automatic scaling and serverless execution.

Benefits over Celery:
- Auto-scaling (up to 1000+ concurrent executions)
- No server management
- Pay-per-use pricing
- Built-in retry mechanisms
- Integrates with API Gateway for REST endpoints
"""

import json
import boto3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os
import logging
from typing import List, Dict, Any, Optional
import time

# Configure logging for Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class LambdaAffiliationQuery:
    """AWS Lambda function for affiliation analysis"""
    
    def __init__(self):
        # Database connection using environment variables or AWS Secrets Manager
        self.engine = self._create_db_connection()
    
    def _create_db_connection(self):
        """Create database connection for Lambda"""
        try:
            # Option 1: Environment variables (simpler)
            if all(key in os.environ for key in ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASS']):
                connection_string = (
                    f"postgresql://{os.environ['DB_USER']}:"
                    f"{os.environ['DB_PASS']}@"
                    f"{os.environ['DB_HOST']}:"
                    f"{os.environ.get('DB_PORT', '5432')}/"
                    f"{os.environ['DB_NAME']}"
                )
                return create_engine(connection_string, pool_pre_ping=True)
            
            # Option 2: AWS Secrets Manager (more secure)
            else:
                return self._create_db_from_secrets()
                
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            raise
    
    def _create_db_from_secrets(self):
        """Create database connection from AWS Secrets Manager"""
        secrets_client = boto3.client('secretsmanager')
        
        try:
            # Get database credentials from Secrets Manager
            secret_response = secrets_client.get_secret_value(
                SecretId=os.environ.get('DB_SECRET_NAME', 'augur-db-credentials')
            )
            credentials = json.loads(secret_response['SecretString'])
            
            connection_string = (
                f"postgresql://{credentials['username']}:"
                f"{credentials['password']}@"
                f"{credentials['host']}:"
                f"{credentials.get('port', '5432')}/"
                f"{credentials['dbname']}"
            )
            
            return create_engine(connection_string, pool_pre_ping=True)
            
        except Exception as e:
            logger.error(f"Failed to get credentials from Secrets Manager: {e}")
            raise
    
    def query_affiliation_data(self, repo_ids: List[int]) -> pd.DataFrame:
        """
        Execute affiliation query (same as 8Knot's affiliation_query)
        
        Args:
            repo_ids: List of repository IDs to query
            
        Returns:
            DataFrame with affiliation data
        """
        logger.info(f"Querying affiliation data for {len(repo_ids)} repositories")
        
        # Same query as 8Knot's affiliation_query.py
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
                c.repo_id = ANY(:repo_ids)
                and timezone('utc', c.created_at) < now()
            GROUP BY c.cntrb_id, c.created_at, c.repo_id, c.login, c.action, c.rank, con.cntrb_company
            ORDER BY c.created_at
        """
        
        try:
            df = pd.read_sql_query(query, self.engine, params={'repo_ids': repo_ids})
            logger.info(f"Retrieved {len(df)} affiliation records")
            return df
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise
    
    def process_affiliation_data(self, df: pd.DataFrame, min_contributions: int = 1) -> pd.DataFrame:
        """Process affiliation data (same logic as 8Knot visualization)"""
        if df.empty:
            return pd.DataFrame()
        
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


def lambda_handler(event, context):
    """
    AWS Lambda handler function
    
    Event structure:
    {
        "operation": "affiliation_chart" | "affiliation_table" | "affiliation_data",
        "repo_ids": [1, 2, 3],
        "min_contributions": 1,
        "email_filter": ["gmail.com", "github.com"]  # optional
    }
    """
    try:
        start_time = time.time()
        
        # Parse event
        operation = event.get('operation', 'affiliation_chart')
        repo_ids = event.get('repo_ids', [])
        min_contributions = event.get('min_contributions', 1)
        email_filter = event.get('email_filter', [])
        
        # Validate input
        if not repo_ids:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'No repository IDs provided',
                    'success': False
                })
            }
        
        if len(repo_ids) > 50:  # Reasonable limit
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Too many repositories (max 50)',
                    'success': False
                })
            }
        
        # Initialize query engine
        query_engine = LambdaAffiliationQuery()
        
        # Execute query
        df_raw = query_engine.query_affiliation_data(repo_ids)
        
        if df_raw.empty:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': 'No affiliation data found',
                    'success': False,
                    'repo_ids': repo_ids
                })
            }
        
        # Process data
        df_processed = query_engine.process_affiliation_data(df_raw, min_contributions)
        
        # Apply email filters
        if email_filter:
            df_processed = df_processed[~df_processed['domains'].isin(email_filter)]
        
        # Generate response based on operation
        if operation == 'affiliation_chart':
            # Create Plotly bar chart
            fig = px.bar(
                df_processed, 
                x="domains", 
                y="occurrences",
                title="Organization Activity by Email Domain",
                labels={"domains": "Email Domains", "occurrences": "Contributions"}
            )
            response_data = fig.to_dict()
            
        elif operation == 'affiliation_table':
            # Create Plotly table
            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=["Organization (Email Domain)", "Contributions"],
                    fill_color='paleturquoise',
                    align='left'
                ),
                cells=dict(
                    values=[df_processed.domains, df_processed.occurrences],
                    fill_color='lightcyan',
                    align='left'
                )
            )])
            fig.update_layout(title="Organization Activity by Email Domain")
            response_data = fig.to_dict()
            
        elif operation == 'affiliation_data':
            # Return raw processed data
            response_data = df_processed.to_dict(orient='records')
            
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': f'Unknown operation: {operation}',
                    'success': False
                })
            }
        
        processing_time = time.time() - start_time
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # For CORS
            },
            'body': json.dumps({
                'success': True,
                'operation': operation,
                'repo_count': len(repo_ids),
                'data_rows': len(df_processed),
                'processing_time_seconds': round(processing_time, 2),
                'data': response_data
            })
        }
        
    except Exception as e:
        logger.error(f"Lambda execution failed: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'success': False
            })
        }


# Example event for testing
EXAMPLE_EVENT = {
    "operation": "affiliation_chart",
    "repo_ids": [1, 2, 3],
    "min_contributions": 2,
    "email_filter": ["gmail.com"]
}

if __name__ == "__main__":
    # Local testing
    context = {}
    result = lambda_handler(EXAMPLE_EVENT, context)
    print(json.dumps(result, indent=2)) 