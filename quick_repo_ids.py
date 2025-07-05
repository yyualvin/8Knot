#!/usr/bin/env python3
"""
Quick script to get repo IDs that have language data
"""
import os
import pandas as pd
import sqlalchemy as sa

# Quick connection
def get_repo_ids_with_languages():
    try:
        # Get credentials from environment
        user = os.getenv("AUGUR_USERNAME")
        password = os.getenv("AUGUR_PASSWORD") 
        host = os.getenv("AUGUR_HOST")
        port = os.getenv("AUGUR_PORT")
        database = os.getenv("AUGUR_DATABASE")
        schema = os.getenv("AUGUR_SCHEMA")
        
        # Connect
        engine = sa.create_engine(
            f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}",
            connect_args={"options": f"-csearch_path={schema}"}
        )
        
        # Simple query to get repo IDs with language data
        query = """
        SELECT DISTINCT 
            repo_id, 
            (SELECT repo_name FROM repo WHERE repo_id = erl.repo_id) as name
        FROM explorer_repo_languages erl 
        ORDER BY repo_id 
        LIMIT 10
        """
        
        df = pd.read_sql(sa.text(query), engine)
        
        print("Repository IDs with language data:")
        print("-" * 40)
        for _, row in df.iterrows():
            print(f"ID: {row['repo_id']:4d} - {row['name']}")
        
        print(f"\n✅ Try these IDs: {', '.join(map(str, df['repo_id'].tolist()))}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    get_repo_ids_with_languages() 