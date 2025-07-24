# 8Knot Search API

A simple Flask API that replicates the search functionality of the 8Knot application. This API provides endpoints to search for repositories and organizations in the same format as the main 8Knot application.

## Setup

1. Install dependencies:
```bash
pip install -r requirements-api.txt
```

2. Set up environment variables (same as 8Knot):
```bash
export AUGUR_USERNAME="your_username"
export AUGUR_PASSWORD="your_password"
export AUGUR_HOST="your_host"
export AUGUR_PORT="your_port"
export AUGUR_DATABASE="your_database"
export AUGUR_SCHEMA="your_schema"
```

3. Run the API:
```bash
python search.py
```

The API will start on port 5001 by default. You can change this by setting the `PORT` environment variable.

## Endpoints

### Health Check
- **GET** `/health`
- Returns the health status of the API and Augur connection

### Search
- **GET** `/api/search?q=<query>&limit=<limit>&threshold=<threshold>&prefix=<prefix>`
- Parameters:
  - `q`: Search query string
  - `limit`: Maximum number of results (default: 100)
  - `threshold`: Fuzzy search threshold 0-1 (default: 0.2)
  - `prefix`: Filter by type ('repo', 'org', or empty for all)
- Returns: List of matching options with `label` and `value` keys

### Get All Repositories
- **GET** `/api/repos`
- Returns: List of all repositories with `repo:` prefix

### Get All Organizations
- **GET** `/api/orgs`
- Returns: List of all organizations with `org:` prefix

### Get All Options
- **GET** `/api/options`
- Returns: List of all available options (repos + orgs) with appropriate prefixes

### Convert Selections to Repo IDs
- **POST** `/api/convert`
- Request body: `{"selections": [repo_ids, org_names]}`
- Returns: List of repo IDs that correspond to the selections

## Example Usage

### Search for repositories containing "django":
```bash
curl "http://localhost:5001/api/search?q=django&prefix=repo"
```

### Search for organizations containing "mozilla":
```bash
curl "http://localhost:5001/api/search?q=mozilla&prefix=org"
```

### Get all repositories:
```bash
curl "http://localhost:5001/api/repos"
```

### Convert selections to repo IDs:
```bash
curl -X POST "http://localhost:5001/api/convert" \
  -H "Content-Type: application/json" \
  -d '{"selections": [12345, "mozilla"]}'
```

## Response Format

All endpoints return JSON responses. The search endpoints return data in the same format as the 8Knot application:

```json
[
  {
    "label": "repo: https://github.com/user/repo",
    "value": 12345
  },
  {
    "label": "org: Mozilla",
    "value": "mozilla"
  }
]
```

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (missing parameters)
- `500`: Internal server error (database connection issues, etc.)

Error responses include an `error` field with a description of the issue. 