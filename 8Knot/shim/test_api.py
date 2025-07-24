#!/usr/bin/env python3
"""
Simple test script to demonstrate the 8Knot Search API functionality.
This script makes example requests to the API endpoints.
"""

import requests
import json
import sys

# API base URL
BASE_URL = "http://localhost:5001"

def test_health():
    """Test the health check endpoint."""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API. Make sure it's running on localhost:5001")
        return False

def test_get_repos():
    """Test getting all repositories."""
    print("Testing get all repositories...")
    try:
        response = requests.get(f"{BASE_URL}/api/repos")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            repos = response.json()
            print(f"Found {len(repos)} repositories")
            if repos:
                print("First 20 repositories:")
                for i, repo in enumerate(repos[:20]):
                    print(f"  {i+1}. {repo}")
        else:
            print(f"Error: {response.json()}")
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_orgs():
    """Test getting all organizations."""
    print("Testing get all organizations...")
    try:
        response = requests.get(f"{BASE_URL}/api/orgs")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            orgs = response.json()
            print(f"Found {len(orgs)} organizations")
            if orgs:
                print(f"First org: {orgs[0]}")
        else:
            print(f"Error: {response.json()}")
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_search(query, prefix=None, limit=5):
    """Test the search endpoint."""
    print(f"Testing search for '{query}'...")
    try:
        params = {"q": query, "limit": limit}
        if prefix:
            params["prefix"] = prefix
            print(f"Filtering by prefix: {prefix}")
        
        response = requests.get(f"{BASE_URL}/api/search", params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            results = response.json()
            print(f"Found {len(results)} results")
            for i, result in enumerate(results[:3]):  # Show first 3 results
                print(f"  {i+1}. {result}")
            if len(results) > 3:
                print(f"  ... and {len(results) - 3} more")
        else:
            print(f"Error: {response.json()}")
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_convert_selections(selections):
    """Test converting selections to repo IDs."""
    print(f"Testing convert selections: {selections}")
    try:
        data = {"selections": selections}
        response = requests.post(f"{BASE_URL}/api/convert", json=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Result: {result}")
        else:
            print(f"Error: {response.json()}")
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_advanced_search(query, algorithm='token_sort', prefix=None, limit=5):
    """Test the advanced search endpoint with different algorithms."""
    print(f"Testing advanced search for '{query}' with algorithm '{algorithm}'...")
    try:
        params = {"q": query, "algorithm": algorithm, "limit": limit, "include_scores": "true"}
        if prefix:
            params["prefix"] = prefix
            print(f"Filtering by prefix: {prefix}")
        
        response = requests.get(f"{BASE_URL}/api/search/advanced", params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            results = data["results"]
            metadata = data["metadata"]
            print(f"Found {len(results)} results")
            print(f"Algorithm: {metadata['algorithm']}")
            print(f"Algorithm description: {metadata['algorithm_description']}")
            for i, result in enumerate(results[:3]):  # Show first 3 results
                score_info = f" (score: {result.get('score', 'N/A')})" if 'score' in result else ""
                print(f"  {i+1}. {result['label']}{score_info}")
            if len(results) > 3:
                print(f"  ... and {len(results) - 3} more")
        else:
            print(f"Error: {response.json()}")
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_compare_algorithms(query, prefix=None, limit=3):
    """Test comparing different fuzzy search algorithms."""
    print(f"Testing algorithm comparison for '{query}'...")
    try:
        params = {"q": query, "limit": limit}
        if prefix:
            params["prefix"] = prefix
            print(f"Filtering by prefix: {prefix}")
        
        response = requests.get(f"{BASE_URL}/api/search/compare", params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            comparison = data["comparison"]
            metadata = data["metadata"]
            print(f"Comparing {len(comparison)} algorithms:")
            
            for alg_name, results in comparison.items():
                print(f"\n  {alg_name.upper()} ({len(results)} results):")
                for i, result in enumerate(results[:2]):  # Show first 2 results per algorithm
                    score_info = f" (score: {result.get('score', 'N/A')})" if 'score' in result else ""
                    print(f"    {i+1}. {result['label']}{score_info}")
                if len(results) > 2:
                    print(f"    ... and {len(results) - 2} more")
        else:
            print(f"Error: {response.json()}")
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_search_with_scores(query, prefix=None, limit=5):
    """Test the enhanced search endpoint with scores included."""
    print(f"Testing search with scores for '{query}'...")
    try:
        params = {"q": query, "limit": limit, "include_scores": "true"}
        if prefix:
            params["prefix"] = prefix
            print(f"Filtering by prefix: {prefix}")
        
        response = requests.get(f"{BASE_URL}/api/search", params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            results = data["results"]
            metadata = data["metadata"]
            print(f"Found {len(results)} results")
            print(f"Query: '{metadata['query']}' -> '{metadata['search_query']}'")
            print(f"Threshold: {metadata['threshold']}")
            for i, result in enumerate(results[:3]):  # Show first 3 results
                score_info = ""
                if 'score' in result:
                    score_info = f" (score: {result['score']})"
                    if 'scores' in result:
                        scores = result['scores']
                        score_info += f" [exact:{scores['exact']}, starts:{scores['starts_with']}, contains:{scores['contains']}, fuzzy:{scores['fuzzy']}]"
                print(f"  {i+1}. {result['label']}{score_info}")
            if len(results) > 3:
                print(f"  ... and {len(results) - 3} more")
        else:
            print(f"Error: {response.json()}")
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_all_data(format_type='detailed'):
    """Test getting all data for client-side processing."""
    print(f"Testing get all data with format '{format_type}'...")
    try:
        params = {"format": format_type, "include_metadata": "true"}
        response = requests.get(f"{BASE_URL}/api/data", params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            
            if format_type == 'simple':
                items = data.get("items", [])
                print(f"Found {len(items)} total items")
                print("Sample items:")
                for i, item in enumerate(items[:5]):
                    print(f"  {i+1}. {item['label']} (type: {item['type']})")
                if len(items) > 5:
                    print(f"  ... and {len(items) - 5} more")
                    
            elif format_type == 'categorized':
                repos = data.get("repositories", [])
                orgs = data.get("organizations", [])
                print(f"Found {len(repos)} repositories and {len(orgs)} organizations")
                print("Sample repositories:")
                for i, repo in enumerate(repos[:3]):
                    print(f"  {i+1}. {repo['label']}")
                print("Sample organizations:")
                for i, org in enumerate(orgs[:3]):
                    print(f"  {i+1}. {org['label']}")
                    
            else:  # detailed
                repos = data.get("repositories", [])
                orgs = data.get("organizations", [])
                all_items = data.get("all_items", [])
                metadata = data.get("metadata", {})
                
                print(f"Found {len(repos)} repositories and {len(orgs)} organizations")
                print(f"Total items: {len(all_items)}")
                if metadata:
                    print(f"Dataset info: {metadata.get('dataset_info', {}).get('description', 'N/A')}")
                    print(f"Recommended libraries: {metadata.get('dataset_info', {}).get('recommended_client_libraries', [])}")
                
                print("Sample items from combined list:")
                for i, item in enumerate(all_items[:5]):
                    print(f"  {i+1}. {item['label']} (type: {item['type']})")
                if len(all_items) > 5:
                    print(f"  ... and {len(all_items) - 5} more")
        else:
            print(f"Error: {response.json()}")
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_client_search(query, prefix=None, limit=10):
    """Test the client-side search endpoint."""
    print(f"Testing client search for '{query}'...")
    try:
        params = {"q": query, "limit": limit, "include_scores": "true"}
        if prefix:
            params["prefix"] = prefix
            print(f"Filtering by prefix: {prefix}")
        
        response = requests.get(f"{BASE_URL}/api/search/client", params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            results = data["results"]
            metadata = data["metadata"]
            print(f"Found {len(results)} results")
            print(f"Search type: {metadata['search_type']}")
            print(f"Recommendation: {metadata['recommendation']}")
            for i, result in enumerate(results[:5]):  # Show first 5 results
                score_info = f" (score: {result.get('score', 'N/A')})" if 'score' in result else ""
                match_type = f" [{result.get('match_type', 'N/A')}]" if 'match_type' in result else ""
                print(f"  {i+1}. {result['label']}{score_info}{match_type}")
            if len(results) > 5:
                print(f"  ... and {len(results) - 5} more")
        else:
            print(f"Error: {response.json()}")
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def interactive_mode():
    """Interactive mode with infinite while loop for user input."""
    print("\n=== 8Knot Search API Interactive Mode ===")
    print("Commands:")
    print("  search <query> [prefix] [limit] - Search for repos/orgs")
    print("  search-scores <query> [prefix] [limit] - Search with detailed scores")
    print("  advanced <query> <algorithm> [prefix] [limit] - Advanced fuzzy search")
    print("  compare <query> [prefix] [limit] - Compare all algorithms")
    print("  get-data [format] - Get all data for client-side processing")
    print("  client-search <query> [prefix] [limit] - Client-side search")
    print("  repos - Get all repositories")
    print("  orgs - Get all organizations")
    print("  convert <selection1> <selection2> ... - Convert selections to repo IDs")
    print("  health - Check API health")
    print("  help - Show this help")
    print("  quit/exit - Exit the program")
    print()
    print("Fuzzy Search Algorithms:")
    print("  token_sort - Sorts tokens before comparing (default)")
    print("  partial - Best partial string matching")
    print("  ratio - Simple string similarity ratio")
    print("  token_set - Compares token sets")
    print("  token_ratio - Token-based ratio")
    print()
    print("Data Formats:")
    print("  simple - Flat list of all items")
    print("  categorized - Separated repos and orgs")
    print("  detailed - Full data with combined list (default)")
    print()
    
    while True:
        try:
            user_input = input("8Knot> ").strip()
            
            if not user_input:
                continue
                
            parts = user_input.split()
            command = parts[0].lower()
            
            if command in ['quit', 'exit']:
                print("Goodbye!")
                break
                
            elif command == 'help':
                print("Commands:")
                print("  search <query> [prefix] [limit] - Search for repos/orgs")
                print("  search-scores <query> [prefix] [limit] - Search with detailed scores")
                print("  advanced <query> <algorithm> [prefix] [limit] - Advanced fuzzy search")
                print("  compare <query> [prefix] [limit] - Compare all algorithms")
                print("  get-data [format] - Get all data for client-side processing")
                print("  client-search <query> [prefix] [limit] - Client-side search")
                print("  repos - Get all repositories")
                print("  orgs - Get all organizations")
                print("  convert <selection1> <selection2> ... - Convert selections to repo IDs")
                print("  health - Check API health")
                print("  help - Show this help")
                print("  quit/exit - Exit the program")
                print()
                print("Fuzzy Search Algorithms:")
                print("  token_sort - Sorts tokens before comparing (default)")
                print("  partial - Best partial string matching")
                print("  ratio - Simple string similarity ratio")
                print("  token_set - Compares token sets")
                print("  token_ratio - Token-based ratio")
                
            elif command == 'health':
                test_health()
                
            elif command == 'repos':
                test_get_repos()
                
            elif command == 'orgs':
                test_get_orgs()
                
            elif command == 'search':
                if len(parts) < 2:
                    print("Usage: search <query> [prefix] [limit]")
                    print("Example: search python")
                    print("Example: search mozilla org 10")
                    continue
                    
                query = parts[1]
                prefix = None
                limit = 5
                
                if len(parts) > 2:
                    # Check if second argument is a prefix
                    if parts[2] in ['repo', 'org']:
                        prefix = parts[2]
                        if len(parts) > 3:
                            try:
                                limit = int(parts[3])
                            except ValueError:
                                print("Limit must be a number")
                                continue
                    else:
                        # Second argument might be a limit
                        try:
                            limit = int(parts[2])
                        except ValueError:
                            print("Limit must be a number")
                            continue
                            
                test_search(query, prefix, limit)
                
            elif command == 'convert':
                if len(parts) < 2:
                    print("Usage: convert <selection1> <selection2> ...")
                    print("Example: convert 12345 mozilla")
                    continue
                    
                selections = parts[1:]
                # Try to convert numeric strings to integers
                for i, selection in enumerate(selections):
                    try:
                        selections[i] = int(selection)
                    except ValueError:
                        # Keep as string if not numeric
                        pass
                        
                test_convert_selections(selections)
                
            elif command == 'search-scores':
                if len(parts) < 2:
                    print("Usage: search-scores <query> [prefix] [limit]")
                    print("Example: search-scores python")
                    print("Example: search-scores mozilla org 10")
                    continue
                    
                query = parts[1]
                prefix = None
                limit = 5
                
                if len(parts) > 2:
                    # Check if second argument is a prefix
                    if parts[2] in ['repo', 'org']:
                        prefix = parts[2]
                        if len(parts) > 3:
                            try:
                                limit = int(parts[3])
                            except ValueError:
                                print("Limit must be a number")
                                continue
                    else:
                        # Second argument might be a limit
                        try:
                            limit = int(parts[2])
                        except ValueError:
                            print("Limit must be a number")
                            continue
                            
                test_search_with_scores(query, prefix, limit)
                
            elif command == 'advanced':
                if len(parts) < 3:
                    print("Usage: advanced <query> <algorithm> [prefix] [limit]")
                    print("Example: advanced python token_sort")
                    print("Example: advanced mozilla partial org 10")
                    print("Algorithms: token_sort, partial, ratio, token_set, token_ratio")
                    continue
                    
                query = parts[1]
                algorithm = parts[2]
                prefix = None
                limit = 5
                
                if len(parts) > 3:
                    # Check if third argument is a prefix
                    if parts[3] in ['repo', 'org']:
                        prefix = parts[3]
                        if len(parts) > 4:
                            try:
                                limit = int(parts[4])
                            except ValueError:
                                print("Limit must be a number")
                                continue
                    else:
                        # Third argument might be a limit
                        try:
                            limit = int(parts[3])
                        except ValueError:
                            print("Limit must be a number")
                            continue
                            
                test_advanced_search(query, algorithm, prefix, limit)
                
            elif command == 'compare':
                if len(parts) < 2:
                    print("Usage: compare <query> [prefix] [limit]")
                    print("Example: compare python")
                    print("Example: compare mozilla org 5")
                    continue
                    
                query = parts[1]
                prefix = None
                limit = 3
                
                if len(parts) > 2:
                    # Check if second argument is a prefix
                    if parts[2] in ['repo', 'org']:
                        prefix = parts[2]
                        if len(parts) > 3:
                            try:
                                limit = int(parts[3])
                            except ValueError:
                                print("Limit must be a number")
                                continue
                    else:
                        # Second argument might be a limit
                        try:
                            limit = int(parts[2])
                        except ValueError:
                            print("Limit must be a number")
                            continue
                            
                test_compare_algorithms(query, prefix, limit)
                
            elif command == 'get-data':
                if len(parts) < 2:
                    print("Usage: get-data [simple|categorized|detailed]")
                    print("Example: get-data simple")
                    print("Example: get-data detailed")
                    continue
                    
                format_type = parts[1]
                test_get_all_data(format_type)
                
            elif command == 'client-search':
                if len(parts) < 2:
                    print("Usage: client-search <query> [prefix] [limit]")
                    print("Example: client-search python")
                    print("Example: client-search mozilla org 10")
                    continue
                    
                query = parts[1]
                prefix = None
                limit = 10
                
                if len(parts) > 2:
                    # Check if second argument is a prefix
                    if parts[2] in ['repo', 'org']:
                        prefix = parts[2]
                        if len(parts) > 3:
                            try:
                                limit = int(parts[3])
                            except ValueError:
                                print("Limit must be a number")
                                continue
                    else:
                        # Second argument might be a limit
                        try:
                            limit = int(parts[2])
                        except ValueError:
                            print("Limit must be a number")
                            continue
                            
                test_client_search(query, prefix, limit)
                
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break

def main():
    """Run all tests."""
    print("8Knot Search API Test Script")
    print("=" * 40)
    print()
    
    # Test health check first
    if not test_health():
        print("API is not available. Please start the API server first.")
        sys.exit(1)
    
    # Check if user wants interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_mode()
        return
    
    # Run automated tests
    print("Running automated tests...")
    
    # Test basic endpoints
    test_get_repos()
    test_get_orgs()
    
    # Test search functionality
    test_search("python")
    test_search("mozilla", prefix="org")
    test_search("django", prefix="repo")
    
    # Test enhanced fuzzy search features
    print("\nTesting enhanced fuzzy search features...")
    test_search_with_scores("python")
    test_advanced_search("python", "partial")
    test_compare_algorithms("python")
    
    # Test conversion (this will fail if no valid selections are provided)
    # You may need to replace these with actual values from your database
    test_convert_selections([12345, "mozilla"])
    
    # Test client-side data fetching
    print("\nTesting client-side data fetching...")
    test_get_all_data()
    test_get_all_data('simple')
    test_get_all_data('categorized')
    
    # Test client-side search
    print("\nTesting client-side search...")
    test_client_search("python")
    test_client_search("mozilla", prefix="org")
    test_client_search("django", prefix="repo")
    
    print("Test completed!")
    print("\nTo run in interactive mode, use: python test_api.py --interactive")

if __name__ == "__main__":
    main() 