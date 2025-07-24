#!/usr/bin/env python3
"""
Simple test script to demonstrate the 8Knot Data API functionality.
This script tests the client-side data approach.
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

def test_get_all_data():
    """Test getting all data for client-side processing."""
    print("Testing get all data...")
    try:
        params = {"include_metadata": "true"}
        response = requests.get(f"{BASE_URL}/api/data", params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            
            repos = data.get("repositories", [])
            orgs = data.get("organizations", [])
            all_items = data.get("all_items", [])
            metadata = data.get("metadata", {})
            
            print(f"Found {len(repos)} repositories and {len(orgs)} organizations")
            print(f"Total items: {len(all_items)}")
            if metadata:
                print(f"Dataset info: {metadata.get('dataset_info', {}).get('description', 'N/A')}")
                print(f"Recommended libraries: {metadata.get('dataset_info', {}).get('recommended_client_libraries', [])}")
            
            print("Sample repositories:")
            for i, repo in enumerate(repos[:3]):
                print(f"  {i+1}. {repo['label']}")
            
            print("Sample organizations:")
            for i, org in enumerate(orgs[:3]):
                print(f"  {i+1}. {org['label']}")
            
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

def test_convert_selections(selections):
    """Test converting selections to repo IDs."""
    print(f"Testing convert selections: {selections}")
    try:
        data = {"selections": selections}
        response = requests.post(f"{BASE_URL}/api/convert", json=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            repo_ids = result.get("repo_ids", [])
            metadata = result.get("metadata", {})
            print(f"Converted to {len(repo_ids)} repo IDs: {repo_ids}")
            if metadata:
                print(f"Input selections: {metadata.get('input_selections', [])}")
                print(f"Repo selections: {metadata.get('repo_selections', [])}")
                print(f"Org selections: {metadata.get('org_selections', [])}")
        else:
            print(f"Error: {response.json()}")
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def interactive_mode():
    """Interactive mode with infinite while loop for user input."""
    print("\n=== 8Knot Data API Interactive Mode ===")
    print("Commands:")
    print("  get-data - Get all data for client-side processing")
    print("  convert <selection1> <selection2> ... - Convert selections to repo IDs")
    print("  health - Check API health")
    print("  help - Show this help")
    print("  quit/exit - Exit the program")
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
                print("  get-data - Get all data for client-side processing")
                print("  convert <selection1> <selection2> ... - Convert selections to repo IDs")
                print("  health - Check API health")
                print("  help - Show this help")
                print("  quit/exit - Exit the program")
                print()
                
            elif command == 'health':
                test_health()
                
            elif command == 'get-data':
                test_get_all_data()
                
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
    print("8Knot Data API Test Script")
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
    
    # Test data fetching
    print("\nTesting data fetching...")
    test_get_all_data()
    
    # Test conversion (this will fail if no valid selections are provided)
    # You may need to replace these with actual values from your database
    print("\nTesting conversion...")
    test_convert_selections([12345, "mozilla"])
    
    print("Test completed!")
    print("\nTo run in interactive mode, use: python test_api.py --interactive")

if __name__ == "__main__":
    main() 