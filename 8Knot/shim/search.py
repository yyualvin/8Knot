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
    - include_scores: Include match scores in response (default: false)
    - sort_by_score: Sort results by match score (default: true)
    - exact_match_first: Prioritize exact matches (default: true)
    
    Returns:
    - List of matching options with 'label' and 'value' keys
    - Optionally includes 'score' field if include_scores=true
    """
    try:
        if augur_manager is None:
            return jsonify({"error": "AugurManager not initialized"}), 500
        
        # Get query parameters
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 100))
        threshold = float(request.args.get('threshold', 0.2))
        prefix = request.args.get('prefix', '').lower()
        include_scores = request.args.get('include_scores', 'false').lower() == 'true'
        sort_by_score = request.args.get('sort_by_score', 'true').lower() == 'true'
        exact_match_first = request.args.get('exact_match_first', 'true').lower() == 'true'
        
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
        
        # If exact match first is enabled, prioritize exact matches
        if exact_match_first and len(search_query) > 2:
            exact_matches = []
            partial_matches = []
            query_lower = search_query.lower()
            
            for opt in matched_options:
                if opt["label"].lower() == query_lower:
                    exact_matches.append(opt)
                elif opt["label"].lower().startswith(query_lower):
                    partial_matches.append(opt)
                else:
                    partial_matches.append(opt)
            
            # Reorder: exact matches first, then partial matches, then fuzzy matches
            matched_options = exact_matches + partial_matches
        
        # If include_scores is requested, calculate and add scores
        if include_scores:
            from rapidfuzz import fuzz
            scored_options = []
            
            for opt in matched_options:
                # Calculate different types of scores
                exact_score = 1.0 if opt["label"].lower() == search_query.lower() else 0.0
                starts_with_score = 1.0 if opt["label"].lower().startswith(search_query.lower()) else 0.0
                contains_score = 1.0 if search_query.lower() in opt["label"].lower() else 0.0
                fuzzy_score = fuzz.token_sort_ratio(search_query.lower(), opt["label"].lower()) / 100.0
                
                # Create a weighted score
                weighted_score = max(exact_score, starts_with_score * 0.9, contains_score * 0.7, fuzzy_score * 0.5)
                
                scored_opt = opt.copy()
                scored_opt["score"] = round(weighted_score, 3)
                scored_opt["scores"] = {
                    "exact": round(exact_score, 3),
                    "starts_with": round(starts_with_score, 3),
                    "contains": round(contains_score, 3),
                    "fuzzy": round(fuzzy_score, 3)
                }
                scored_options.append(scored_opt)
            
            matched_options = scored_options
            
            # Sort by score if requested
            if sort_by_score:
                matched_options.sort(key=lambda x: x["score"], reverse=True)
        
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
        
        # Add metadata to response
        response_data = {
            "results": result,
            "metadata": {
                "query": query,
                "search_query": search_query,
                "prefix_type": prefix_type,
                "threshold": threshold,
                "total_found": len(result),
                "limit": limit
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logging.error(f"Error in search endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/search/advanced', methods=['GET'])
def advanced_search():
    """
    Advanced search endpoint for testing different fuzzy search algorithms.
    
    Query parameters:
    - q: Search query string
    - limit: Maximum number of results (default: 20)
    - threshold: Fuzzy search threshold (default: 0.2)
    - prefix: Filter by prefix type ('repo', 'org', or None for all)
    - algorithm: Fuzzy search algorithm ('token_sort', 'partial', 'ratio', 'token_set', 'token_ratio')
    - include_scores: Include match scores in response (default: true)
    
    Returns:
    - Detailed search results with scores and algorithm information
    """
    try:
        if augur_manager is None:
            return jsonify({"error": "AugurManager not initialized"}), 500
        
        # Get query parameters
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 20))
        threshold = float(request.args.get('threshold', 0.2))
        prefix = request.args.get('prefix', '').lower()
        algorithm = request.args.get('algorithm', 'token_sort').lower()
        include_scores = request.args.get('include_scores', 'true').lower() == 'true'
        
        if not query:
            return jsonify({"error": "Query parameter 'q' is required"}), 400
        
        # Validate algorithm parameter
        valid_algorithms = {
            'token_sort': 'token_sort_ratio',
            'partial': 'partial_ratio', 
            'ratio': 'ratio',
            'token_set': 'token_set_ratio',
            'token_ratio': 'token_ratio'
        }
        
        if algorithm not in valid_algorithms:
            return jsonify({"error": f"Invalid algorithm. Must be one of: {list(valid_algorithms.keys())}"}), 400
        
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
        
        # Import rapidfuzz for advanced scoring
        from rapidfuzz import fuzz, process
        
        # Get the appropriate scorer function
        scorer_func = getattr(fuzz, valid_algorithms[algorithm])
        
        # Convert threshold to the 0-100 scale used by rapidfuzz
        threshold_100 = int(threshold * 100)
        
        # Perform advanced fuzzy search
        matches = process.extract(
            search_query,
            [opt["label"] for opt in options],
            scorer=scorer_func,
            processor=str.lower,  # Case-insensitive matching
            limit=limit * 2,  # Get more results for filtering
            score_cutoff=threshold_100,
        )
        
        # Map back to original option objects with scores
        options_dict = {opt["label"]: opt for opt in options}
        scored_options = []
        
        for match_data in matches:
            label = match_data[0]
            score = match_data[1] / 100.0  # Convert to 0-1 scale
            
            if label in options_dict:
                opt = options_dict[label].copy()
                opt["score"] = round(score, 3)
                opt["algorithm"] = algorithm
                scored_options.append(opt)
        
        # Filter by prefix type if specified
        if prefix_type == "repo":
            scored_options = [opt for opt in scored_options if isinstance(opt["value"], int)]
        elif prefix_type == "org":
            scored_options = [opt for opt in scored_options if isinstance(opt["value"], str)]
        
        # Sort by score
        scored_options.sort(key=lambda x: x["score"], reverse=True)
        
        # Format options with prefixes based on their type
        formatted_opts = []
        seen_values = set()  # Track seen values to prevent duplicates
        
        for opt in scored_options:
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
        
        # Add metadata to response
        response_data = {
            "results": result,
            "metadata": {
                "query": query,
                "search_query": search_query,
                "prefix_type": prefix_type,
                "algorithm": algorithm,
                "threshold": threshold,
                "total_found": len(result),
                "limit": limit,
                "algorithm_description": {
                    "token_sort": "Sorts tokens in both strings before comparing",
                    "partial": "Best partial string matching",
                    "ratio": "Simple string similarity ratio",
                    "token_set": "Compares token sets",
                    "token_ratio": "Token-based ratio"
                }[algorithm]
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logging.error(f"Error in advanced search endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/search/compare', methods=['GET'])
def compare_search_algorithms():
    """
    Compare different fuzzy search algorithms on the same query.
    
    Query parameters:
    - q: Search query string
    - limit: Maximum number of results per algorithm (default: 5)
    - threshold: Fuzzy search threshold (default: 0.2)
    - prefix: Filter by prefix type ('repo', 'org', or None for all)
    
    Returns:
    - Results from all algorithms for comparison
    """
    try:
        if augur_manager is None:
            return jsonify({"error": "AugurManager not initialized"}), 500
        
        # Get query parameters
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 5))
        threshold = float(request.args.get('threshold', 0.2))
        prefix = request.args.get('prefix', '').lower()
        
        if not query:
            return jsonify({"error": "Query parameter 'q' is required"}), 400
        
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
        
        # Import rapidfuzz
        from rapidfuzz import fuzz, process
        
        # Define algorithms to compare
        algorithms = {
            'token_sort': fuzz.token_sort_ratio,
            'partial': fuzz.partial_ratio,
            'ratio': fuzz.ratio,
            'token_set': fuzz.token_set_ratio,
            'token_ratio': fuzz.token_ratio
        }
        
        # Convert threshold to the 0-100 scale used by rapidfuzz
        threshold_100 = int(threshold * 100)
        
        comparison_results = {}
        
        for alg_name, scorer_func in algorithms.items():
            # Perform search with this algorithm
            matches = process.extract(
                search_query,
                [opt["label"] for opt in options],
                scorer=scorer_func,
                processor=str.lower,
                limit=limit * 2,
                score_cutoff=threshold_100,
            )
            
            # Map back to original option objects with scores
            options_dict = {opt["label"]: opt for opt in options}
            scored_options = []
            
            for match_data in matches:
                label = match_data[0]
                score = match_data[1] / 100.0
                
                if label in options_dict:
                    opt = options_dict[label].copy()
                    opt["score"] = round(score, 3)
                    scored_options.append(opt)
            
            # Filter by prefix type if specified
            if prefix_type == "repo":
                scored_options = [opt for opt in scored_options if isinstance(opt["value"], int)]
            elif prefix_type == "org":
                scored_options = [opt for opt in scored_options if isinstance(opt["value"], str)]
            
            # Sort by score and limit
            scored_options.sort(key=lambda x: x["score"], reverse=True)
            scored_options = scored_options[:limit]
            
            # Format options with prefixes
            formatted_opts = []
            seen_values = set()
            
            for opt in scored_options:
                if opt["value"] in seen_values:
                    continue
                
                seen_values.add(opt["value"])
                formatted_opt = opt.copy()
                if isinstance(opt["value"], str):
                    formatted_opt["label"] = f"org: {opt['label']}"
                else:
                    formatted_opt["label"] = f"repo: {opt['label']}"
                formatted_opts.append(formatted_opt)
            
            comparison_results[alg_name] = formatted_opts
        
        # Add metadata
        response_data = {
            "comparison": comparison_results,
            "metadata": {
                "query": query,
                "search_query": search_query,
                "prefix_type": prefix_type,
                "threshold": threshold,
                "limit": limit,
                "algorithms": list(algorithms.keys())
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logging.error(f"Error in compare search algorithms endpoint: {str(e)}")
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


@app.route('/api/data', methods=['GET'])
def get_all_data():
    """
    Get all repositories and organizations in a well-formatted structure for client-side processing.
    This is similar to the client-side cache approach used in the main 8Knot application.
    
    Query parameters:
    - format: Response format ('simple', 'detailed', 'categorized') (default: 'detailed')
    - include_metadata: Include metadata about the dataset (default: true)
    
    Returns:
    - Well-formatted list of all repos and orgs with metadata
    """
    try:
        if augur_manager is None:
            return jsonify({"error": "AugurManager not initialized"}), 500
        
        format_type = request.args.get('format', 'detailed').lower()
        include_metadata = request.args.get('include_metadata', 'true').lower() == 'true'
        
        # Get all available options
        options = augur_manager.get_multiselect_options().copy()
        
        # Separate repos and orgs
        repos = []
        orgs = []
        
        for opt in options:
            if isinstance(opt["value"], int):
                # It's a repo
                repo_data = {
                    "label": opt["label"],
                    "value": opt["value"],
                    "type": "repo",
                    "formatted_label": f"repo: {opt['label']}"
                }
                repos.append(repo_data)
            else:
                # It's an org
                org_data = {
                    "label": opt["label"],
                    "value": opt["value"],
                    "type": "org",
                    "formatted_label": f"org: {opt['label']}"
                }
                orgs.append(org_data)
        
        # Sort by label for consistent ordering
        repos.sort(key=lambda x: x["label"].lower())
        orgs.sort(key=lambda x: x["label"].lower())
        
        # Prepare response based on format
        if format_type == 'simple':
            # Simple flat list with type indicators
            all_items = []
            for repo in repos:
                all_items.append({
                    "label": repo["formatted_label"],
                    "value": repo["value"],
                    "type": "repo"
                })
            for org in orgs:
                all_items.append({
                    "label": org["formatted_label"],
                    "value": org["value"],
                    "type": "org"
                })
            
            response_data = {"items": all_items}
            
        elif format_type == 'categorized':
            # Categorized by type
            response_data = {
                "repositories": repos,
                "organizations": orgs
            }
            
        else:  # detailed (default)
            # Detailed format with full information
            response_data = {
                "repositories": repos,
                "organizations": orgs,
                "all_items": []  # Combined list for easy client-side processing
            }
            
            # Add combined list for easy searching
            for repo in repos:
                response_data["all_items"].append({
                    "label": repo["formatted_label"],
                    "value": repo["value"],
                    "type": "repo",
                    "original_label": repo["label"]
                })
            for org in orgs:
                response_data["all_items"].append({
                    "label": org["formatted_label"],
                    "value": org["value"],
                    "type": "org",
                    "original_label": org["label"]
                })
        
        # Add metadata if requested
        if include_metadata:
            metadata = {
                "total_repositories": len(repos),
                "total_organizations": len(orgs),
                "total_items": len(repos) + len(orgs),
                "format": format_type,
                "last_updated": augur_manager.get_last_update_time() if hasattr(augur_manager, 'get_last_update_time') else None,
                "dataset_info": {
                    "description": "Complete dataset of repositories and organizations for client-side search",
                    "usage": "Use this data for client-side fuzzy search and filtering",
                    "recommended_client_libraries": ["rapidfuzz", "fuse.js", "fuse.js"]
                }
            }
            response_data["metadata"] = metadata
        
        return jsonify(response_data)
        
    except Exception as e:
        logging.error(f"Error in get_all_data endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/search/client', methods=['GET'])
def client_search():
    """
    Client-side search endpoint that returns search results for client-side processing.
    This endpoint performs basic filtering and returns results that can be further
    processed by the client using their preferred fuzzy search library.
    
    Query parameters:
    - q: Search query string
    - limit: Maximum number of results (default: 50)
    - prefix: Filter by prefix type ('repo', 'org', or None for all)
    - include_scores: Include basic match scores (default: false)
    
    Returns:
    - Filtered results suitable for client-side fuzzy search
    """
    try:
        if augur_manager is None:
            return jsonify({"error": "AugurManager not initialized"}), 500
        
        # Get query parameters
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 50))
        prefix = request.args.get('prefix', '').lower()
        include_scores = request.args.get('include_scores', 'false').lower() == 'true'
        
        if not query:
            return jsonify({"error": "Query parameter 'q' is required"}), 400
        
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
        
        # Filter by prefix type if specified
        if prefix_type == "repo":
            options = [opt for opt in options if isinstance(opt["value"], int)]
        elif prefix_type == "org":
            options = [opt for opt in options if isinstance(opt["value"], str)]
        
        # Perform basic filtering (exact, starts_with, contains)
        # This provides a good starting point for client-side fuzzy search
        filtered_options = []
        query_lower = search_query.lower()
        
        for opt in options:
            label_lower = opt["label"].lower()
            
            # Calculate basic match score
            exact_match = label_lower == query_lower
            starts_with = label_lower.startswith(query_lower)
            contains = query_lower in label_lower
            
            if exact_match or starts_with or contains:
                result_item = {
                    "label": opt["label"],
                    "value": opt["value"],
                    "type": "repo" if isinstance(opt["value"], int) else "org",
                    "formatted_label": f"{'repo' if isinstance(opt["value"], int) else 'org'}: {opt['label']}"
                }
                
                if include_scores:
                    # Simple scoring for client-side processing
                    score = 1.0 if exact_match else (0.9 if starts_with else 0.7)
                    result_item["score"] = round(score, 3)
                    result_item["match_type"] = "exact" if exact_match else ("starts_with" if starts_with else "contains")
                
                filtered_options.append(result_item)
        
        # Sort by relevance (exact matches first, then starts_with, then contains)
        if include_scores:
            filtered_options.sort(key=lambda x: x["score"], reverse=True)
        else:
            # Sort alphabetically if no scores
            filtered_options.sort(key=lambda x: x["label"].lower())
        
        # Limit results
        result = filtered_options[:limit]
        
        # Add metadata
        response_data = {
            "results": result,
            "metadata": {
                "query": query,
                "search_query": search_query,
                "prefix_type": prefix_type,
                "total_found": len(result),
                "limit": limit,
                "search_type": "client_side_filtered",
                "recommendation": "Use client-side fuzzy search libraries (rapidfuzz, fuse.js) for better results"
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logging.error(f"Error in client_search endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Initialize AugurManager before starting the server
    if initialize_augur_manager():
        port = int(os.environ.get('PORT', 5001))
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        logging.error("Failed to initialize AugurManager. Exiting.")
        sys.exit(1)
