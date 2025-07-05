#!/usr/bin/env python3
"""
Simple script to discover and get repository IDs from Augur database
"""

import os
import sys
import pandas as pd
import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError

def get_database_connection():
    """Create database connection"""
    try:
        user = os.getenv("AUGUR_USERNAME")
        password = os.getenv("AUGUR_PASSWORD")
        host = os.getenv("AUGUR_HOST")
        port = os.getenv("AUGUR_PORT")
        database = os.getenv("AUGUR_DATABASE")
        schema = os.getenv("AUGUR_SCHEMA")
        
        if not all([user, password, host, port, database, schema]):
            print("❌ Missing environment variables. Please set:")
            print("   AUGUR_USERNAME, AUGUR_PASSWORD, AUGUR_HOST")
            print("   AUGUR_PORT, AUGUR_DATABASE, AUGUR_SCHEMA")
            return None
        
        connection_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
        engine = sa.create_engine(
            connection_string,
            connect_args={"options": f"-csearch_path={schema}"}
        )
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(sa.text("SELECT 1"))
        
        return engine
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def show_all_repos(engine, limit=20):
    """Show all repositories in the database"""
    query = """
    SELECT 
        r.repo_id,
        r.repo_name,
        r.repo_git,
        rg.rg_name as organization,
        r.repo_status,
        r.repo_added::date as added_date
    FROM repo r
    JOIN repo_groups rg ON r.repo_group_id = rg.repo_group_id
    ORDER BY r.repo_name
    LIMIT %(limit)s
    """
    
    try:
        df = pd.read_sql(sa.text(query), engine, params={"limit": limit})
        print(f"\n📋 ALL REPOSITORIES (showing first {limit}):")
        print("=" * 80)
        print(df.to_string(index=False))
        return df
    except Exception as e:
        print(f"❌ Error fetching repositories: {e}")
        return pd.DataFrame()

def show_repos_with_language_data(engine, limit=20):
    """Show repositories that have language data"""
    query = """
    SELECT 
        r.repo_id,
        r.repo_name,
        r.repo_git,
        rg.rg_name as organization,
        COUNT(DISTINCT erl.programming_language) as languages_count,
        SUM(erl.files) as total_files,
        SUM(erl.code_lines) as total_lines
    FROM repo r
    JOIN repo_groups rg ON r.repo_group_id = rg.repo_group_id
    JOIN explorer_repo_languages erl ON r.repo_id = erl.repo_id
    GROUP BY r.repo_id, r.repo_name, r.repo_git, rg.rg_name
    ORDER BY total_files DESC
    LIMIT %(limit)s
    """
    
    try:
        df = pd.read_sql(sa.text(query), engine, params={"limit": limit})
        print(f"\n📊 REPOSITORIES WITH LANGUAGE DATA (top {limit} by file count):")
        print("=" * 100)
        print(df.to_string(index=False))
        return df
    except Exception as e:
        print(f"❌ Error fetching repositories with language data: {e}")
        return pd.DataFrame()

def show_repos_by_organization(engine, org_name=None):
    """Show repositories by organization"""
    if org_name:
        query = """
        SELECT 
            r.repo_id,
            r.repo_name,
            r.repo_git,
            rg.rg_name as organization
        FROM repo r
        JOIN repo_groups rg ON r.repo_group_id = rg.repo_group_id
        WHERE LOWER(rg.rg_name) LIKE LOWER(%(org_pattern)s)
        ORDER BY r.repo_name
        """
        params = {"org_pattern": f"%{org_name}%"}
    else:
        # Show all organizations
        query = """
        SELECT 
            rg.rg_name as organization,
            COUNT(r.repo_id) as repo_count
        FROM repo r
        JOIN repo_groups rg ON r.repo_group_id = rg.repo_group_id
        GROUP BY rg.rg_name
        ORDER BY repo_count DESC
        """
        params = {}
    
    try:
        df = pd.read_sql(sa.text(query), engine, params=params)
        if org_name:
            print(f"\n🏢 REPOSITORIES IN ORGANIZATION '{org_name}':")
        else:
            print(f"\n🏢 ALL ORGANIZATIONS:")
        print("=" * 60)
        print(df.to_string(index=False))
        return df
    except Exception as e:
        print(f"❌ Error fetching organization data: {e}")
        return pd.DataFrame()

def search_repos(engine, search_term):
    """Search repositories by name"""
    query = """
    SELECT 
        r.repo_id,
        r.repo_name,
        r.repo_git,
        rg.rg_name as organization
    FROM repo r
    JOIN repo_groups rg ON r.repo_group_id = rg.repo_group_id
    WHERE LOWER(r.repo_name) LIKE LOWER(%(search_pattern)s)
       OR LOWER(r.repo_git) LIKE LOWER(%(search_pattern)s)
    ORDER BY r.repo_name
    LIMIT 20
    """
    
    try:
        df = pd.read_sql(
            sa.text(query), 
            engine, 
            params={"search_pattern": f"%{search_term}%"}
        )
        print(f"\n🔍 SEARCH RESULTS FOR '{search_term}':")
        print("=" * 60)
        if df.empty:
            print("No repositories found matching your search.")
        else:
            print(df.to_string(index=False))
        return df
    except Exception as e:
        print(f"❌ Error searching repositories: {e}")
        return pd.DataFrame()

def main():
    """Main function with interactive menu"""
    print("🔍 Repository ID Discovery Tool")
    print("=" * 40)
    
    # Connect to database
    engine = get_database_connection()
    if not engine:
        return
    
    print("✅ Database connected successfully!")
    
    while True:
        print("\n📋 MENU:")
        print("1. Show all repositories")
        print("2. Show repositories with language data")
        print("3. Show organizations")
        print("4. Show repos by organization")
        print("5. Search repositories")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            limit = input("How many repos to show? (default 20): ").strip()
            limit = int(limit) if limit.isdigit() else 20
            show_all_repos(engine, limit)
            
        elif choice == '2':
            limit = input("How many repos to show? (default 20): ").strip()
            limit = int(limit) if limit.isdigit() else 20
            df = show_repos_with_language_data(engine, limit)
            if not df.empty:
                print(f"\n💡 TIP: Good repo IDs to try: {', '.join(map(str, df['repo_id'].head(5).tolist()))}")
            
        elif choice == '3':
            show_repos_by_organization(engine)
            
        elif choice == '4':
            org_name = input("Enter organization name (or part of it): ").strip()
            if org_name:
                show_repos_by_organization(engine, org_name)
            
        elif choice == '5':
            search_term = input("Enter search term: ").strip()
            if search_term:
                search_repos(engine, search_term)
                
        elif choice == '6':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 