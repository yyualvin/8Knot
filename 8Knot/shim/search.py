"""
Simple API that replicates the search functionality of 8Knot.
Provides endpoints to search for repos and orgs in the same format as index_callbacks.
"""
import os
import sys
import logging
import json
from flask import Flask, request, jsonify
from typing import List, Dict, Any
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the parent directory to the path so we can import from 8Knot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_manager.augur_manager import AugurManager
from pages.index.search_utils import fuzzy_search

# Configure logging
logging.basicConfig(format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)

# Global AugurManager instance
augur_manager = None


def initialize_augur_manager():
    """Initialize the AugurManager with database connection."""
    global augur_manager
    try:
        # Hardcode localhost:5411
        os.environ["AUGUR_HOST"] = "localhost"
        os.environ["AUGUR_PORT"] = "5432"
        
        # Create augur manager object
        augur_manager = AugurManager(handles_oauth=False)
        
        # Create engine
        engine = augur_manager.get_engine()
        
        # Initialize multiselect options
        augur_manager.multiselect_startup()
        
        logging.info("AugurManager initialized successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to initialize AugurManager: {str(e)}")
        return False


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "augur_connected": augur_manager is not None
    })


@app.route('/api/search', methods=['GET'])
def search():
    """
    Search endpoint that replicates the functionality of dynamic_multiselect_options.
    
    Query parameters:
    - q: Search query string
    - limit: Maximum number of results (default: 100)
    - threshold: Fuzzy search threshold (default: 0.2)
    - prefix: Filter by prefix type ('repo', 'org', or None for all)
    
    Returns:
    - List of matching options with 'label' and 'value' keys
    """
    try:
        if augur_manager is None:
            return jsonify({"error": "AugurManager not initialized"}), 500
        
        # Get query parameters
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 100))
        threshold = float(request.args.get('threshold', 0.2))
        prefix = request.args.get('prefix', '').lower()
        
        if not query:
            return jsonify([])
        
        # Get all available options
        options = augur_manager.get_multiselect_options().copy()
        
        # Remove prefixes from the search query if present
        search_query = query
        prefix_type = None
        
        if search_query.lower().startswith("repo:"):
            search_query = search_query[5:].strip()
            prefix_type = "repo"
        elif search_query.lower().startswith("org:"):
            search_query = search_query[4:].strip()
            prefix_type = "org"
        
        # Override with explicit prefix parameter if provided
        if prefix:
            prefix_type = prefix
        
        # Perform fuzzy search
        matched_options = fuzzy_search(search_query, options, threshold=threshold)
        
        # Filter by prefix type if specified
        if prefix_type == "repo":
            matched_options = [opt for opt in matched_options if isinstance(opt["value"], int)]
        elif prefix_type == "org":
            matched_options = [opt for opt in matched_options if isinstance(opt["value"], str)]
        
        # Format options with prefixes based on their type
        formatted_opts = []
        seen_values = set()  # Track seen values to prevent duplicates
        
        for opt in matched_options:
            # Skip duplicates (based on value)
            if opt["value"] in seen_values:
                continue
            
            seen_values.add(opt["value"])
            formatted_opt = opt.copy()
            if isinstance(opt["value"], str):
                # It's an org
                formatted_opt["label"] = f"org: {opt['label']}"
            else:
                # It's a repo
                formatted_opt["label"] = f"repo: {opt['label']}"
            formatted_opts.append(formatted_opt)
        
        # Limit results
        result = formatted_opts[:limit]
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error in search endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/repos', methods=['GET'])
def get_repos():
    """
    Get all repositories in the same format as index_callbacks.
    
    Returns:
    - List of repo options with 'label' and 'value' keys
    """
    try:
        if augur_manager is None:
            return jsonify({"error": "AugurManager not initialized"}), 500
        
        options = augur_manager.get_multiselect_options()
        repos = [opt for opt in options if isinstance(opt["value"], int)]
        
        # Format with repo: prefix
        formatted_repos = []
        for repo in repos:
            formatted_repo = repo.copy()
            formatted_repo["label"] = f"repo: {repo['label']}"
            formatted_repos.append(formatted_repo)
        
        return jsonify(formatted_repos)
        
    except Exception as e:
        logging.error(f"Error in get_repos endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/orgs', methods=['GET'])
def get_orgs():
    """
    Get all organizations in the same format as index_callbacks.
    
    Returns:
    - List of org options with 'label' and 'value' keys
    """
    try:
        if augur_manager is None:
            return jsonify({"error": "AugurManager not initialized"}), 500
        
        options = augur_manager.get_multiselect_options()
        orgs = [opt for opt in options if isinstance(opt["value"], str)]
        
        # Format with org: prefix
        formatted_orgs = []
        for org in orgs:
            formatted_org = org.copy()
            formatted_org["label"] = f"org: {org['label']}"
            formatted_orgs.append(formatted_org)
        
        return jsonify(formatted_orgs)
        
    except Exception as e:
        logging.error(f"Error in get_orgs endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/options', methods=['GET'])
def get_all_options():
    """
    Get all available options (repos + orgs) in the same format as index_callbacks.
    
    Returns:
    - List of all options with 'label' and 'value' keys
    """
    try:
        if augur_manager is None:
            return jsonify({"error": "AugurManager not initialized"}), 500
        
        options = augur_manager.get_multiselect_options().copy()
        
        # Format with appropriate prefixes
        formatted_options = []
        for opt in options:
            formatted_opt = opt.copy()
            if isinstance(opt["value"], str):
                # It's an org
                formatted_opt["label"] = f"org: {opt['label']}"
            else:
                # It's a repo
                formatted_opt["label"] = f"repo: {opt['label']}"
            formatted_options.append(formatted_opt)
        
        return jsonify(formatted_options)
        
    except Exception as e:
        logging.error(f"Error in get_all_options endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/convert', methods=['POST'])
def convert_selections():
    """
    Convert selected values to repo IDs, similar to multiselect_values_to_repo_ids.
    
    Request body:
    - selections: List of selected values (repo IDs and org names)
    
    Returns:
    - List of repo IDs that correspond to the selections
    """
    try:
        if augur_manager is None:
            return jsonify({"error": "AugurManager not initialized"}), 500
        
        data = request.get_json()
        if not data or 'selections' not in data:
            return jsonify({"error": "Missing 'selections' in request body"}), 400
        
        user_vals = data['selections']
        
        if not user_vals:
            return jsonify({"error": "No selections provided"}), 400
        
        # Individual repo numbers
        repos = [r for r in user_vals if isinstance(r, int)]
        
        # Names of augur groups or orgs
        names = [n for n in user_vals if isinstance(n, str)]
        
        # Get repos from orgs
        org_repos = [augur_manager.org_to_repos(o) for o in names if augur_manager.is_org(o)]
        # Flatten list repo_ids in orgs to 1D
        org_repos = [v for l in org_repos for v in l]
        
        # Only unique repo ids
        all_repo_ids = list(set().union(*[repos, org_repos]))
        
        return jsonify({
            "repo_ids": all_repo_ids,
            "repos": repos,
            "org_repos": org_repos
        })
        
    except Exception as e:
        logging.error(f"Error in convert_selections endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Initialize AugurManager before starting the server
    if initialize_augur_manager():
        port = int(os.environ.get('PORT', 5001))
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        logging.error("Failed to initialize AugurManager. Exiting.")
        sys.exit(1)
