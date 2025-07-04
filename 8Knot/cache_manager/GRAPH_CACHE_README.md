# Graph Caching System Documentation

## Overview

The Graph Caching System provides dramatic performance improvements by caching serialized plotly graphs in Redis. This eliminates the need to reprocess data and regenerate graphs for repeated requests with the same parameters.

## Performance Benefits

- **100-1000x faster** response times for cached graphs
- **Eliminates pandas processing overhead** (the biggest bottleneck)
- **Reduces CPU and memory usage** on the server
- **Minimal storage overhead** with gzip compression
- **Perfect for static data sources** like the 8Knot PostgreSQL cache

## Architecture

```
User Request → Graph Cache Check → [HIT: Return Cached Graph] OR [MISS: Generate + Cache + Return]
```

The system uses a three-layer approach:
1. **Graph Cache** (Redis) - Serialized plotly JSON with gzip compression
2. **Data Cache** (PostgreSQL + Redis) - Existing raw data caching  
3. **Source Database** (Augur) - Original data source

## Quick Start

### 1. Adding Graph Caching to a Visualization

**Option A: Function-based approach (Recommended)**

```python
from cache_manager.graph_cache_utils import with_graph_caching, extract_viz_params

@callback(...)
def my_visualization_graph(repolist, interval, start_date):
    # Wait for data availability (existing code)
    while not_cached := cf.get_uncached(func_name=my_query.__name__, repolist=repolist):
        time.sleep(0.5)
    
    # Create cache parameters
    params = extract_viz_params(
        repolist=repolist, 
        interval=interval, 
        start_date=start_date
    )
    
    def generate_graph():
        """Generate the graph when not cached"""
        # Existing graph generation code here
        df = cf.retrieve_from_cache(...)
        processed_df = process_data(df, ...)
        fig = create_figure(processed_df, ...)
        return fig
    
    # Use graph caching
    return with_graph_caching(VIZ_ID, params, generate_graph)
```

**Option B: Decorator approach**

```python
from cache_manager.graph_cache_utils import cached_visualization

@cached_visualization("my-visualization-id")
def my_visualization_graph(repolist, interval):
    # Existing code unchanged
    # Caching happens automatically
    return fig
```

### 2. Cache Key Parameters

The `extract_viz_params()` function handles common parameter types:

```python
params = extract_viz_params(
    repolist=[1, 2, 3],           # Lists are sorted for consistency
    interval="M",                 # Strings, ints, floats, bools
    start_date="2023-01-01",      # Dates converted to strings
    bot_switch=True,              # Boolean flags
    custom_param=complex_object   # Other types converted to strings
)
```

## Administration

### View Cache Statistics

```bash
cd 8Knot/cache_manager
python -m graph_cache_admin stats                    # Overall stats
python -m graph_cache_admin stats commits-over-time  # Specific visualization
python -m graph_cache_admin list                     # List all cached visualizations
```

### Clear Cache

```bash
python -m graph_cache_admin clear commits-over-time  # Clear specific visualization
python -m graph_cache_admin clear-all               # Clear all cached graphs
```

### Monitor Performance

```bash
python -m graph_cache_admin monitor 300             # Monitor for 5 minutes
python -m graph_cache_admin info                    # Show configuration
```

## Examples

### Example 1: Simple Visualization

```python
# Before (8Knot/pages/contributions/visualizations/commits_over_time.py)
def commits_over_time_graph(repolist, interval):
    while not_cached := cf.get_uncached(func_name=cmq.__name__, repolist=repolist):
        time.sleep(0.5)
    
    df = cf.retrieve_from_cache(tablename=cmq.__name__, repolist=repolist)
    df_processed = process_data(df, interval)
    fig = create_figure(df_processed, interval)
    return fig

# After (with graph caching)
def commits_over_time_graph(repolist, interval):
    while not_cached := cf.get_uncached(func_name=cmq.__name__, repolist=repolist):
        time.sleep(0.5)
    
    params = extract_viz_params(repolist=repolist, interval=interval)
    
    def generate_graph():
        df = cf.retrieve_from_cache(tablename=cmq.__name__, repolist=repolist)
        df_processed = process_data(df, interval)
        fig = create_figure(df_processed, interval)
        return fig
    
    return with_graph_caching(VIZ_ID, params, generate_graph)
```

### Example 2: Complex Parameters

```python
def complex_visualization_graph(repolist, interval, start_date, end_date, filters):
    # Extract all parameters that affect the graph
    params = extract_viz_params(
        repolist=repolist,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        filters=filters,
        # Add any other parameters that change the graph
    )
    
    def generate_graph():
        # Complex processing logic
        return fig
    
    return with_graph_caching("complex-viz", params, generate_graph)
```

## Technical Details

### Cache Key Generation

Cache keys are generated using MD5 hashes of sorted parameters:

```
Key Format: graph:<viz_id>:<param_hash>
Example: graph:commits-over-time:a1b2c3d4e5f6...
```

### Compression

Plotly JSON is compressed using gzip, typically achieving 70-80% size reduction:

```python
# Typical compression ratios
Original JSON: 15,234 bytes
Compressed:     3,456 bytes  (77% reduction)
```

### Expiration

Cached graphs expire after 7 days by default. Since the PostgreSQL cache is static, this provides a safety margin while maintaining performance.

### Memory Usage

Estimated storage per graph:
- Simple graphs: 1-5 KB compressed
- Complex graphs: 5-20 KB compressed
- Very complex graphs: 20-100 KB compressed

For 1000 cached graphs: ~10-50 MB total

## Migration Guide

### Rolling Out to Existing Visualizations

1. **Start with high-traffic visualizations** (commits over time, issues over time)
2. **Test thoroughly** in development environment
3. **Monitor cache hit rates** and performance improvements
4. **Gradually expand** to other visualizations
5. **Use the admin tools** to monitor cache effectiveness

### Minimal Code Changes Required

The system is designed for minimal disruption:

```python
# Only 3 lines of changes needed:
from cache_manager.graph_cache_utils import with_graph_caching, extract_viz_params  # +1 line

def my_callback(...):
    params = extract_viz_params(...)          # +1 line
    def generate_graph(): ...                 # Wrap existing code
    return with_graph_caching(VIZ_ID, params, generate_graph)  # +1 line
```

### Testing Strategy

1. **Unit tests**: Verify cache hit/miss behavior
2. **Integration tests**: Test with real data and parameters
3. **Performance tests**: Measure response time improvements
4. **Load tests**: Verify cache doesn't cause memory issues

## Troubleshooting

### Common Issues

**Cache Misses Despite Same Parameters**
- Check parameter consistency (list ordering, data types)
- Use `extract_viz_params()` for normalization
- Monitor cache keys with admin tools

**Memory Usage**
- Monitor Redis memory with `info` command
- Adjust expiration times if needed
- Use compression statistics to optimize

**Performance Not Improving**
- Verify caching is enabled and working
- Check cache hit rates
- Ensure expensive operations are inside `generate_graph()`

### Debug Mode

Disable caching for debugging:

```python
@cached_visualization("my-viz", cache_enabled=False)
def my_visualization(...):
    # Caching disabled, normal processing
```

## Best Practices

1. **Include all parameters** that affect graph appearance
2. **Use consistent parameter types** (strings, not objects)
3. **Monitor cache hit rates** regularly
4. **Clear cache after code changes** that affect graph generation
5. **Use admin tools** to monitor memory usage
6. **Test cache behavior** during development

## Future Enhancements

- [ ] Cache warming for popular parameter combinations
- [ ] Automatic cache invalidation on data updates
- [ ] Cache analytics dashboard
- [ ] Distributed caching across multiple Redis instances
- [ ] Smart cache preloading based on user patterns

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Use the admin tools to diagnose cache behavior
3. Check Redis logs for connection issues
4. Monitor performance with the built-in tools 