import logging
import time
from typing import Dict, Any, Callable, Optional
from functools import wraps
import plotly.graph_objects as go
from .graph_cache_manager import GraphCacheManager

# Global instance
_graph_cache_manager = None

def get_graph_cache_manager() -> GraphCacheManager:
    """Get the singleton graph cache manager instance."""
    global _graph_cache_manager
    if _graph_cache_manager is None:
        _graph_cache_manager = GraphCacheManager()
    return _graph_cache_manager

def cached_visualization(viz_id: str, cache_enabled: bool = True):
    """
    Decorator to add graph caching to visualization functions.
    
    Args:
        viz_id: Unique identifier for the visualization
        cache_enabled: Whether to enable caching (useful for debugging)
    
    Usage:
        @cached_visualization("commits-over-time")
        def commits_over_time_graph(repolist, interval):
            # ... existing code ...
            return fig
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not cache_enabled:
                return func(*args, **kwargs)
            
            # Extract parameters for cache key
            params = {
                'args': args,
                'kwargs': kwargs
            }
            
            # Try to get cached graph first
            cache_manager = get_graph_cache_manager()
            cached_fig = cache_manager.get_cached_graph(viz_id, params)
            
            if cached_fig is not None:
                return cached_fig
            
            # Cache miss - generate the graph
            logging.info(f"Cache MISS: {viz_id} - generating graph...")
            start_time = time.perf_counter()
            
            fig = func(*args, **kwargs)
            
            generation_time = time.perf_counter() - start_time
            logging.info(f"Graph generation took {generation_time:.3f}s")
            
            # Cache the result
            if isinstance(fig, go.Figure):
                cache_manager.cache_graph(viz_id, params, fig)
            
            return fig
        
        return wrapper
    return decorator

def with_graph_caching(viz_id: str, params: Dict[str, Any], 
                       generate_func: Callable[[], go.Figure]) -> go.Figure:
    """
    Function-based approach for adding graph caching.
    
    Args:
        viz_id: Unique identifier for the visualization
        params: Dictionary of parameters affecting the graph
        generate_func: Function that generates the graph when not cached
    
    Returns:
        Plotly figure (either cached or newly generated)
    
    Usage:
        def my_visualization(repolist, interval):
            params = {'repolist': repolist, 'interval': interval}
            
            def generate_graph():
                # ... existing graph generation code ...
                return fig
            
            return with_graph_caching("my-viz", params, generate_graph)
    """
    cache_manager = get_graph_cache_manager()
    
    # Try cache first
    cached_fig = cache_manager.get_cached_graph(viz_id, params)
    if cached_fig is not None:
        return cached_fig
    
    # Generate graph
    logging.info(f"Cache MISS: {viz_id} - generating graph...")
    start_time = time.perf_counter()
    
    fig = generate_func()
    
    generation_time = time.perf_counter() - start_time
    logging.info(f"Graph generation took {generation_time:.3f}s")
    
    # Cache the result
    if isinstance(fig, go.Figure):
        cache_manager.cache_graph(viz_id, params, fig)
    
    return fig

def extract_viz_params(**kwargs) -> Dict[str, Any]:
    """
    Extract and normalize parameters for cache keys.
    
    This function handles common parameter types and ensures
    consistent cache key generation.
    """
    params = {}
    
    for key, value in kwargs.items():
        if value is None:
            continue
            
        # Handle list parameters (like repolist)
        if isinstance(value, list):
            # Sort lists to ensure consistent cache keys
            if value and isinstance(value[0], (int, str)):
                params[key] = sorted(value)
            else:
                params[key] = value
        
        # Handle other parameter types
        elif isinstance(value, (str, int, float, bool)):
            params[key] = value
        
        # Convert other types to string
        else:
            params[key] = str(value)
    
    return params

def clear_viz_cache(viz_id: str) -> int:
    """
    Clear all cached graphs for a specific visualization.
    
    Args:
        viz_id: Unique identifier for the visualization
        
    Returns:
        Number of cache entries deleted
    """
    cache_manager = get_graph_cache_manager()
    return cache_manager.invalidate_all_graphs(viz_id)

def get_cache_stats(viz_id: str = None) -> Dict[str, Any]:
    """
    Get caching statistics.
    
    Args:
        viz_id: Optional specific visualization ID
        
    Returns:
        Dictionary with cache statistics
    """
    cache_manager = get_graph_cache_manager()
    return cache_manager.get_cache_stats(viz_id) 