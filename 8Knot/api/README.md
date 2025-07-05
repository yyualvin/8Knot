# 8Knot Modular API

A modular API for generating standalone JSON Plotly visualizations and data queries from the 8Knot codebase. This API transforms the Dash + Celery architecture into clean, standalone functions for FastAPI, Lambda, or direct usage.

## Architecture Overview

The API is organized into several key modules:

```
api/
├── __init__.py              # Main package initialization
├── config.py                # Configuration management
├── base.py                  # Base classes for all components
├── utils.py                 # Utility functions
├── queries/                 # Data query modules
├── visualizations/         # Plotly chart generators
├── metrics/                # Simple metric calculators
└── examples/               # Usage examples
```

## Key Features

- **Modular Design**: Each component is independent and reusable
- **Consistent Patterns**: All modules follow the same base class structure
- **Plotly JSON Output**: All visualizations return JSON-serializable Plotly figures
- **Parameter Support**: Extensive parameterization for customization
- **Error Handling**: Comprehensive error handling and validation
- **8Knot Styling**: Consistent color schemes and templates
- **Direct Database Access**: No caching layer required
- **Type Hints**: Full type annotations for better development experience

## Quick Start

### 1. Configuration

Set up your database connection using environment variables:

```bash
export AUGUR_HOST=localhost
export AUGUR_PORT=5432
export AUGUR_DATABASE=augur
export AUGUR_USERNAME=augur
export AUGUR_PASSWORD=augur
```

### 2. Basic Usage

```python
from api.queries.affiliation_query import AffiliationQuery
from api.visualizations.affiliation_visualization import AffiliationVisualization
from api.metrics.commit_metrics import CommitMetrics

# Example repository IDs
repo_ids = [1, 2, 3]

# Simple query
affiliation_query = AffiliationQuery()
org_data = affiliation_query.get_organization_activity(repo_ids)

# Generate visualization
affiliation_viz = AffiliationVisualization()
chart_result = affiliation_viz.generate_organization_bar_chart(repo_ids)

# Calculate metrics
commit_metrics = CommitMetrics()
total_commits = commit_metrics.get_total_commits(repo_ids)
```

### 3. Chart Types Available

The API supports multiple chart types for each data domain:

```python
# Bar charts
bar_chart = affiliation_viz.generate_organization_bar_chart(repo_ids)

# Pie charts
pie_chart = affiliation_viz.generate_organization_pie_chart(repo_ids)

# Tables
table = affiliation_viz.generate_organization_table(repo_ids)

# Treemaps
treemap = affiliation_viz.create_email_domain_treemap(data)

# Time series
timeline = affiliation_viz.create_contributor_activity_timeline(data)
```

## Module Descriptions

### Configuration (`config.py`)

Manages database connections, styling, and API settings:

- **DatabaseConfig**: Connection strings, pooling, timeouts
- **StyleConfig**: 8Knot color palette, fonts, margins
- **APIConfig**: Validation, caching, limits

Key features:
- Environment variable support
- Connection pooling and testing
- Plotly template generation
- Repository ID validation

### Base Classes (`base.py`)

Provides consistent patterns for all API components:

- **BaseQuery**: SQL execution, validation, response formatting
- **BaseVisualization**: Chart generation, templating, error handling
- **BaseMetric**: Metric calculation with formatting
- **BaseTable/BaseChart**: Specialized visualization bases

### Utilities (`utils.py`)

Common functions used across the API:

- **DateUtils**: Time intervals, date formatting, period calculations
- **FormatUtils**: Number formatting, duration display, string cleaning
- **DataUtils**: Validation, parsing, data processing
- **ValidationUtils**: Parameter validation, range checking
- **ErrorUtils**: Standardized error responses

### Queries (`queries/`)

Data query engines for all 8Knot data sources:

Currently implemented:
- **AffiliationQuery**: Organization/email domain analysis
- **CommitsQuery**: Commit activity and statistics

Planned (based on existing 8Knot queries):
- ContributorsQuery
- IssuesQuery
- PullRequestsQuery
- RepositoryQuery
- And 12 more...

### Visualizations (`visualizations/`)

Plotly chart generators with consistent styling:

Currently implemented:
- **AffiliationVisualization**: Organization charts, tables, treemaps

Each visualization module provides:
- Multiple chart types (bar, pie, table, etc.)
- Data processing and formatting
- Custom styling and theming
- High-level generation methods

### Metrics (`metrics/`)

Simple metric calculators for quick insights:

Currently implemented:
- **CommitMetrics**: Counts, averages, file statistics

Features:
- Fast numerical calculations
- Formatted display values
- Comprehensive summaries
- Error handling

## Usage Patterns

### 1. Direct Data Access

```python
# Get raw data
query = AffiliationQuery()
data = query.get_organization_activity(repo_ids, min_contributions=5)

# Process and use data
processed = query.process_affiliation_data(data, group_threshold=0.05)
```

### 2. Complete Visualization Generation

```python
# One-step chart generation with data fetching
viz = AffiliationVisualization()
result = viz.generate_organization_bar_chart(
    repo_ids, 
    min_contributions=2,
    title="Custom Chart Title"
)

# Result includes chart JSON and metadata
chart_json = result['data']
processing_time = result['processing_time_seconds']
```

### 3. Custom Chart Creation

```python
# Get data separately and create custom chart
viz = AffiliationVisualization()
data = viz.query_engine.get_organization_activity(repo_ids)

# Create custom chart with specific parameters
fig = viz.create_organization_pie_chart(
    data,
    title="Organization Distribution"
)

# Convert to JSON
chart_json = fig.to_dict()
```

### 4. Metrics Dashboard

```python
# Collect multiple metrics
commit_metrics = CommitMetrics()
metrics = commit_metrics.get_commit_metrics_summary(repo_ids)

dashboard = {
    "commits": metrics['total_commits'],
    "authors": metrics['unique_authors'],
    "avg_lines": metrics['avg_lines_added'],
    "formatted": metrics['formatted_values']
}
```

## API Responses

All API functions return consistent response structures:

### Successful Query Response
```python
{
    "success": True,
    "data": [...],  # DataFrame or processed data
    "message": "Query completed successfully",
    "processing_time_seconds": 0.05,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### Successful Visualization Response
```python
{
    "success": True,
    "data": {...},  # Plotly figure JSON
    "message": "Chart generated for 3 repositories",
    "repo_count": 3,
    "data_points": 15,
    "processing_time_seconds": 0.12,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### Error Response
```python
{
    "success": False,
    "error": {
        "type": "ValidationError",
        "message": "Invalid repository IDs",
        "timestamp": "2024-01-01T12:00:00Z"
    }
}
```

## Extending the API

### Adding New Queries

1. Create a new query class inheriting from `BaseQuery`:

```python
class NewQuery(BaseQuery):
    def get_data(self, repo_ids: List[int], **kwargs) -> pd.DataFrame:
        # Implement main query method
        pass
    
    def get_specific_data(self, repo_ids: List[int]) -> pd.DataFrame:
        # Add specific query methods
        query = "SELECT ... FROM ..."
        return self.execute_query(query)
```

2. Add SQL queries using the base class methods
3. Include data processing and validation
4. Update the package `__init__.py`

### Adding New Visualizations

1. Create a visualization class inheriting from base classes:

```python
class NewVisualization(BaseChart, BaseTable):
    def __init__(self, query_engine: NewQuery = None):
        super().__init__(query_engine or NewQuery())
    
    def create_figure(self, df: pd.DataFrame, **kwargs) -> go.Figure:
        # Implement default chart type
        pass
    
    def create_custom_chart(self, df: pd.DataFrame) -> go.Figure:
        # Add specific chart types
        pass
```

2. Implement chart generation methods
3. Add high-level generation methods that include data fetching
4. Apply consistent styling using base class methods

### Adding New Metrics

1. Create a metrics class inheriting from `BaseMetric`:

```python
class NewMetrics(BaseMetric):
    def calculate(self, repo_ids: List[int], **kwargs) -> Union[int, float, str]:
        # Implement default metric
        pass
    
    def get_specific_metric(self, repo_ids: List[int]) -> float:
        # Add specific metric calculations
        pass
```

## Performance Considerations

The API is designed for performance:

- **Direct Database Access**: No caching layer overhead
- **Connection Pooling**: Efficient database connection management
- **Lazy Loading**: Query engines created only when needed
- **Optimized Queries**: Leverages existing materialized views
- **Minimal Dependencies**: Only essential libraries included

Typical performance:
- Simple metrics: 0.05-0.1 seconds
- Data queries: 0.1-0.5 seconds  
- Chart generation: 0.2-1.0 seconds

## Integration Options

### FastAPI Integration

```python
from fastapi import FastAPI
from api.visualizations.affiliation_visualization import AffiliationVisualization

app = FastAPI()
affiliation_viz = AffiliationVisualization()

@app.get("/affiliation/chart/{repo_ids}")
async def get_affiliation_chart(repo_ids: str):
    repo_list = [int(x) for x in repo_ids.split(",")]
    return affiliation_viz.generate_organization_bar_chart(repo_list)
```

### AWS Lambda Integration

```python
import json
from api.visualizations.affiliation_visualization import AffiliationVisualization

def lambda_handler(event, context):
    repo_ids = event['repo_ids']
    affiliation_viz = AffiliationVisualization()
    result = affiliation_viz.generate_organization_bar_chart(repo_ids)
    
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
```

### Jupyter Notebook Integration

```python
import plotly.graph_objects as go
from api.visualizations.affiliation_visualization import AffiliationVisualization

# Generate chart
viz = AffiliationVisualization()
result = viz.generate_organization_bar_chart([1, 2, 3])

# Display in notebook
fig = go.Figure(result['data'])
fig.show()
```

## Dependencies

Core dependencies:
- `pandas`: Data manipulation
- `plotly`: Chart generation
- `sqlalchemy`: Database connections
- `psycopg2-binary`: PostgreSQL driver

Optional dependencies:
- `fastapi`: For web API endpoints
- `uvicorn`: For FastAPI server
- `python-dateutil`: For advanced date handling

## Next Steps

To complete the full 8Knot API transformation:

1. **Implement remaining queries** (16 more based on existing query files)
2. **Create visualization modules** for all chart types from existing pages
3. **Add metrics modules** for all simple metric calculations
4. **Create FastAPI endpoints** that use the modular API functions
5. **Add comprehensive testing** for all modules
6. **Performance optimization** and caching strategies

## Support

For questions or issues:
1. Check the examples in `api/examples/`
2. Review the base class documentation in `api/base.py`
3. Examine existing implementations for patterns
4. Test database connectivity with `config.test_connection()` 