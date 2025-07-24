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
                print(f"First repo: {repos[0]}")
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

def main():
    """Run all tests."""
    print("8Knot Search API Test Script")
    print("=" * 40)
    print()
    
    # Test health check first
    if not test_health():
        print("API is not available. Please start the API server first.")
        sys.exit(1)
    
    # Test basic endpoints
    test_get_repos()
    test_get_orgs()
    
    # Test search functionality
    test_search("python")
    test_search("mozilla", prefix="org")
    test_search("django", prefix="repo")
    
    # Test conversion (this will fail if no valid selections are provided)
    # You may need to replace these with actual values from your database
    test_convert_selections([12345, "mozilla"])
    
    print("Test completed!")

if __name__ == "__main__":
    main() 