import redis
import os
import hashlib
import json
import gzip
import logging
from typing import Dict, Any, Optional
import plotly.graph_objects as go


class GraphCacheManager:
    """
    Manages caching of serialized plotly graphs in Redis.
    
    This provides massive performance improvements by caching the final
    plotly JSON instead of reprocessing data every time.
    """
    
    def __init__(self, decode_responses=False):
        # Redis cache for plotly graphs
        # Note: decode_responses=False is required for binary compressed data
        self._redis = redis.StrictRedis(
            host=os.getenv("REDIS_SERVICE_HOST", "redis-cache"),
            port=os.getenv("REDIS_SERVICE_PORT", "6379"),
            password=os.getenv("REDIS_PASSWORD", ""),
            decode_responses=decode_responses,
        )
        
    def _get_cache_key(self, viz_id: str, params: Dict[str, Any]) -> str:
        """
        Generate a unique cache key for a visualization with specific parameters.
        
        Args:
            viz_id: Unique identifier for the visualization
            params: Dictionary of all parameters that affect the graph
            
        Returns:
            Unique cache key string
        """
        # Sort parameters to ensure consistent hashing
        param_str = json.dumps(params, sort_keys=True, default=str)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()
        return f"graph:{viz_id}:{param_hash}"
    
    def cache_graph(self, viz_id: str, params: Dict[str, Any], fig: go.Figure, expiry_seconds: int = 604800) -> bool:
        """
        Cache a plotly figure with compression.
        
        Args:
            viz_id: Unique identifier for the visualization
            params: Dictionary of parameters used to generate the graph
            fig: Plotly figure object to cache
            expiry_seconds: Cache expiration time (default: 7 days)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cache_key = self._get_cache_key(viz_id, params)
            
            # Serialize and compress the figure
            fig_json = fig.to_json()
            compressed_json = gzip.compress(fig_json.encode('utf-8'))
            
            # Store in Redis with expiration
            success = self._redis.set(cache_key, compressed_json, ex=expiry_seconds)
            
            if success:
                logging.info(f"Cached graph: {viz_id} (key: {cache_key[:16]}...)")
                logging.info(f"Compression ratio: {len(compressed_json)}/{len(fig_json)} = {len(compressed_json)/len(fig_json):.2%}")
            
            return bool(success)
            
        except Exception as e:
            logging.error(f"Failed to cache graph {viz_id}: {str(e)}")
            return False
    
    def get_cached_graph(self, viz_id: str, params: Dict[str, Any]) -> Optional[go.Figure]:
        """
        Retrieve a cached plotly figure.
        
        Args:
            viz_id: Unique identifier for the visualization
            params: Dictionary of parameters used to generate the graph
            
        Returns:
            Plotly figure object if cached, None otherwise
        """
        try:
            cache_key = self._get_cache_key(viz_id, params)
            compressed_json = self._redis.get(cache_key)
            
            if compressed_json is None:
                return None
                
            # Decompress and deserialize
            # Since decode_responses=False, we get bytes directly
            fig_json = gzip.decompress(compressed_json).decode('utf-8')
            fig_dict = json.loads(fig_json)
            
            # Reconstruct plotly figure
            fig = go.Figure(fig_dict)
            
            logging.info(f"Graph cache HIT: {viz_id} (key: {cache_key[:16]}...)")
            return fig
            
        except Exception as e:
            logging.error(f"Failed to retrieve cached graph {viz_id}: {str(e)}")
            return None
    
    def exists(self, viz_id: str, params: Dict[str, Any]) -> bool:
        """
        Check if a graph is cached without retrieving it.
        
        Args:
            viz_id: Unique identifier for the visualization
            params: Dictionary of parameters used to generate the graph
            
        Returns:
            True if cached, False otherwise
        """
        try:
            cache_key = self._get_cache_key(viz_id, params)
            return bool(self._redis.exists(cache_key))
        except Exception as e:
            logging.error(f"Failed to check cache existence for {viz_id}: {str(e)}")
            return False
    
    def invalidate_graph(self, viz_id: str, params: Dict[str, Any]) -> bool:
        """
        Remove a specific cached graph.
        
        Args:
            viz_id: Unique identifier for the visualization
            params: Dictionary of parameters used to generate the graph
            
        Returns:
            True if successfully removed, False otherwise
        """
        try:
            cache_key = self._get_cache_key(viz_id, params)
            result = self._redis.delete(cache_key)
            logging.info(f"Invalidated graph cache: {viz_id}")
            return bool(result)
        except Exception as e:
            logging.error(f"Failed to invalidate graph cache {viz_id}: {str(e)}")
            return False
    
    def invalidate_all_graphs(self, viz_id: str) -> int:
        """
        Remove all cached graphs for a specific visualization.
        
        Args:
            viz_id: Unique identifier for the visualization
            
        Returns:
            Number of keys deleted
        """
        try:
            pattern = f"graph:{viz_id}:*"
            keys = self._redis.keys(pattern)
            if keys:
                deleted = self._redis.delete(*keys)
                logging.info(f"Invalidated {deleted} graph caches for {viz_id}")
                return deleted
            return 0
        except Exception as e:
            logging.error(f"Failed to invalidate all graphs for {viz_id}: {str(e)}")
            return 0
    
    def get_cache_stats(self, viz_id: str = None) -> Dict[str, Any]:
        """
        Get caching statistics.
        
        Args:
            viz_id: Optional specific visualization ID
            
        Returns:
            Dictionary with cache statistics
        """
        try:
            if viz_id:
                pattern = f"graph:{viz_id}:*"
            else:
                pattern = "graph:*"
                
            keys = self._redis.keys(pattern)
            
            stats = {
                'total_graphs': len(keys),
                'pattern': pattern,
                'sample_keys': keys[:5] if keys else []
            }
            
            # Get memory usage for sample keys
            if keys:
                sample_key = keys[0]
                try:
                    memory_usage = self._redis.memory_usage(sample_key)
                    stats['avg_memory_per_graph'] = memory_usage
                    stats['total_memory_estimate'] = memory_usage * len(keys)
                except:
                    # memory_usage not available in all Redis versions
                    pass
                    
            return stats
            
        except Exception as e:
            logging.error(f"Failed to get cache stats: {str(e)}")
            return {'error': str(e)} 