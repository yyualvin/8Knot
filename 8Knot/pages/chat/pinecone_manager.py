import time
import os
import requests
import json
import concurrent.futures
from typing import List, Dict, Any, Optional, Union
from dotenv import load_dotenv
# Load environment variables from env.list file
load_dotenv("env.list")

class PineconeManager:
    """
    Direct Pinecone API client using REST calls instead of the SDK
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        if not self.api_key:
            raise ValueError("Pinecone API key is required")
        
        self.base_url = "https://api.pinecone.io"
        self.headers = {
            "Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def list_indexes(self) -> List[Dict[str, Any]]:
        """List all indexes in the project"""
        try:
            response = requests.get(f"{self.base_url}/indexes", headers=self.headers)
            response.raise_for_status()
            return response.json().get("indexes", [])
        except requests.exceptions.RequestException as e:
            print(f"Error listing indexes: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return []
    
    def create_index(self, name: str, dimension: int, metric: str = "cosine", 
                    cloud: str = "aws", region: str = "us-east-1") -> Dict[str, Any]:
        """Create a new serverless index"""
        data = {
            "name": name,
            "dimension": dimension,
            "metric": metric,
            "spec": {
                "serverless": {
                    "cloud": cloud,
                    "region": region
                }
            }
        }
        
        try:
            response = requests.post(f"{self.base_url}/indexes", 
                                   headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating index: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            raise
    
    def describe_index(self, name: str) -> Optional[Dict[str, Any]]:
        """Get details about a specific index"""
        try:
            response = requests.get(f"{self.base_url}/indexes/{name}", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response and e.response.status_code == 404:
                return None  # Index doesn't exist
            print(f"Error describing index: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return None
    
    def delete_index(self, name: str) -> None:
        """Delete an index"""
        response = requests.delete(f"{self.base_url}/indexes/{name}", headers=self.headers)
        response.raise_for_status()
    
    def get_or_create_index(self, name: str, dimension: int = 1536, 
                          metric: str = "cosine", cloud: str = "aws", 
                          region: str = "us-east-1", wait_until_ready: bool = True):
        """Get an existing index or create a new one if it doesn't exist"""
        # Check if index already exists
        index_info = self.describe_index(name)
        
        if index_info:
            print(f"Index '{name}' already exists")
            if index_info.get("status", {}).get("ready"):
                print(f"Index '{name}' is ready")
            else:
                print(f"Index '{name}' is still initializing...")
        else:
            print(f"Creating new index '{name}' with dimension {dimension}")
            try:
                self.create_index(name, dimension, metric, cloud, region)
                print(f"Index '{name}' creation initiated")
            except Exception as e:
                print(f"Failed to create index: {e}")
                raise
        
        # Wait for index to be ready if requested
        if wait_until_ready:
            print("Waiting for index to be ready...")
            max_attempts = 60  # 5 minutes max
            attempt = 0
            
            while attempt < max_attempts:
                index_info = self.describe_index(name)
                if index_info and index_info.get("status", {}).get("ready"):
                    print(f"Index '{name}' is ready!")
                    break
                    
                print(f"Index still initializing... (attempt {attempt + 1}/{max_attempts})")
                time.sleep(5)
                attempt += 1
            
            if attempt >= max_attempts:
                print("Warning: Index may not be ready yet, but proceeding...")
        
        return self.get_index_client(name)
    
    def get_index_client(self, index_name: str):
        """Get an index client for data operations"""
        index_info = self.describe_index(index_name)
        if not index_info:
            raise ValueError(f"Index '{index_name}' does not exist")
            
        host = index_info["host"]
        # api_key is guaranteed to be str since we check it in __init__
        assert self.api_key is not None
        return PineconeIndexClient(host, self.api_key)


class PineconeIndexClient:
    """
    Direct Pinecone Index API client for data operations
    """
    
    def __init__(self, host: str, api_key: str):
        self.host = host
        self.api_key = api_key
        self.base_url = f"https://{host}"
        self.headers = {
            "Api-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def upsert(self, vectors: List[Dict[str, Any]], namespace: str = "") -> Dict[str, Any]:
        """Upsert vectors into the index"""
        data = {
            "vectors": vectors,
            "namespace": namespace
        }
        
        response = requests.post(f"{self.base_url}/vectors/upsert",
                               headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def query(self, vector: Optional[List[float]] = None, id: Optional[str] = None, 
             top_k: int = 10, namespace: str = "", 
             filter: Optional[Dict[str, Any]] = None, include_values: bool = False,
             include_metadata: bool = True) -> Dict[str, Any]:
        """Query the index for similar vectors"""
        data: Dict[str, Any] = {
            "topK": top_k,
            "namespace": namespace,
            "includeValues": include_values,
            "includeMetadata": include_metadata
        }
        
        if vector:
            data["vector"] = vector
        if id:
            data["id"] = id
        if filter:
            data["filter"] = filter
        
        response = requests.post(f"{self.base_url}/query",
                               headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def fetch(self, ids: List[str], namespace: str = "") -> Dict[str, Any]:
        """Fetch vectors by ID"""
        params = {
            "ids": ids,
            "namespace": namespace
        }
        
        response = requests.get(f"{self.base_url}/vectors/fetch",
                              headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def delete(self, ids: Optional[List[str]] = None, delete_all: bool = False,
              namespace: str = "", filter: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Delete vectors from the index"""
        data: Dict[str, Any] = {"namespace": namespace}
        
        if delete_all:
            data["deleteAll"] = delete_all
        elif ids:
            data["ids"] = ids
        elif filter:
            data["filter"] = filter
        
        response = requests.post(f"{self.base_url}/vectors/delete",
                               headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def describe_index_stats(self, filter: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get statistics about the index"""
        data: Dict[str, Any] = {}
        if filter:
            data["filter"] = filter
        
        response = requests.post(f"{self.base_url}/describe_index_stats",
                               headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()


# Initialize the global Pinecone manager
pc = PineconeManager()

# Convenience function to get default index
def get_default_index():
    """Get or create the default 8Knot index"""
    index_name = os.getenv("PINECONE_INDEX_NAME", "8knot-index")
    dimension = int(os.getenv("PINECONE_DIMENSION", "1536"))  # Default for OpenAI embeddings
    
    return pc.get_or_create_index(
        name=index_name,
        dimension=dimension,
        metric="cosine",
        cloud="aws",
        region="us-east-1"
    )

name = get_default_index()

