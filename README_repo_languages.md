# Repository Languages Analysis - Standalone Example

This standalone example demonstrates how to analyze programming language distribution in repositories using data from an Augur database. It's based on the `repo_languages` functionality from 8Knot.

## Features

- 🔌 **Database Connection**: Connects to Augur PostgreSQL database
- 📊 **Data Analysis**: Processes language data using 8Knot's methodology
- 📈 **Visualization**: Creates interactive Plotly pie charts
- 🎨 **Custom Styling**: Uses 8Knot's color scheme and dark theme
- 💾 **Export Options**: Save charts as HTML files

## What it Does

The script:
1. Connects to your Augur database
2. Queries the `explorer_repo_languages` materialized view
3. Processes the data (grouping small languages into "Other")
4. Creates two pie chart visualizations:
   - Languages by number of files
   - Languages by lines of code
5. Displays interactive charts in your browser

## Prerequisites

### Database Requirements
- Access to an Augur database with the `explorer_repo_languages` materialized view
- PostgreSQL database credentials

### Python Dependencies
Install the required packages:

```bash
pip install pandas plotly sqlalchemy psycopg2-binary
```

Or using a requirements file:

```bash
# requirements.txt
pandas>=1.5.0
plotly>=5.0.0
sqlalchemy>=1.4.0
psycopg2-binary>=2.9.0
```

## Setup

### Environment Variables
Set the following environment variables with your Augur database credentials:

```bash
export AUGUR_USERNAME=your_db_username
export AUGUR_PASSWORD=your_db_password
export AUGUR_HOST=your_db_host
export AUGUR_PORT=your_db_port
export AUGUR_DATABASE=your_db_name
export AUGUR_SCHEMA=your_db_schema
```

### Database Schema
The script expects the `explorer_repo_languages` materialized view to exist in your database. This view should contain:
- `repo_id`: Repository identifier
- `programming_language`: Programming language name
- `code_lines`: Number of lines of code
- `files`: Number of files

## Usage

### Basic Usage
```bash
python repo_languages_example.py
```

### Interactive Flow
1. **Repository Selection**: The script will show available repositories and ask you to select which ones to analyze
2. **Analysis**: It will query and process the language data
3. **Visualization**: Two pie charts will open in your browser
4. **Export**: Optionally save the charts as HTML files

### Example Output
```
Repository Languages Analysis - Standalone Example
Based on 8Knot functionality

Available repositories:
   repo_id       repo_name organization
         1    awesome-repo   my-org
         2    cool-project   other-org
         3    data-science   research-group

Enter repository IDs to analyze (comma-separated):
Example: 1,2,3
Repository IDs: 1,2

==================================================
REPOSITORY LANGUAGE ANALYSIS SUMMARY
==================================================
Total repositories analyzed: 2
Total language records: 15
Unique languages found: 8
Languages after processing: 6

Total files: 1,234
Total lines of code: 45,678

Top 5 languages by files:
  Python: 456 files (37.0%)
  JavaScript: 321 files (26.0%)
  CSS: 234 files (19.0%)
  HTML: 123 files (10.0%)
  Markdown: 78 files (6.3%)
```

## How it Works

### Data Processing (8Knot Methodology)
1. **SVG Handling**: SVG files are treated as having one line of code per file
2. **Grouping**: Languages are grouped by name and their metrics are summed
3. **Small Language Filtering**: Languages with <0.1% of total files are grouped as "Other"
4. **Sorting**: Results are sorted by file count (descending)
5. **Percentages**: Calculates percentage distributions

### Visualization
- **Interactive Pie Charts**: Hover for detailed information
- **Custom Colors**: Uses 8Knot's color palette
- **Dark Theme**: Slate theme with custom colors
- **Two Views**: Files vs. Lines of Code perspective

## Database Schema Reference

The `explorer_repo_languages` materialized view is typically created with:

```sql
SELECT
    e.repo_id,
    augur_data.repo.repo_git,
    augur_data.repo.repo_name,
    e.programming_language,
    e.code_lines,
    e.files
FROM
    augur_data.repo,
    (SELECT
        d.repo_id,
        d.programming_language,
        SUM(d.code_lines) AS code_lines,
        COUNT(*)::int AS files
    FROM
        (SELECT
            augur_data.repo_labor.repo_id,
            augur_data.repo_labor.programming_language,
            augur_data.repo_labor.code_lines
        FROM
            augur_data.repo_labor,
            ( SELECT
                    augur_data.repo_labor.repo_id,
                    MAX ( data_collection_date ) AS last_collected
                FROM
                    augur_data.repo_labor
                GROUP BY augur_data.repo_labor.repo_id) recent
        WHERE
            augur_data.repo_labor.repo_id = recent.repo_id
            AND augur_data.repo_labor.data_collection_date > recent.last_collected - (5 * interval '1 minute')) d
    GROUP BY d.repo_id, d.programming_language) e
WHERE augur_data.repo.repo_id = e.repo_id
ORDER BY e.repo_id
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check your environment variables
   - Verify database credentials
   - Ensure the database is accessible

2. **No Language Data Found**
   - Verify the `explorer_repo_languages` view exists
   - Check if the selected repositories have language data
   - Ensure the materialized view is populated

3. **Charts Not Opening**
   - Ensure you have a default browser set
   - Check if ports are blocked
   - Try saving as HTML and opening manually

### Environment Variable Template
Create a `.env` file or add to your shell profile:

```bash
# Augur Database Configuration
export AUGUR_USERNAME=augur_user
export AUGUR_PASSWORD=your_password
export AUGUR_HOST=localhost
export AUGUR_PORT=5432
export AUGUR_DATABASE=augur
export AUGUR_SCHEMA=augur_data
```

## Customization

### Color Scheme
Modify the `COLOR_SEQUENCE` list to change colors:

```python
COLOR_SEQUENCE = [
    "#B5B682",  # sage
    "#c0bc5d",  # citron (yellow-ish)
    "#6C8975",  # reseda green
    # Add your colors here
]
```

### Filtering Logic
Adjust the minimum file threshold:

```python
# Change 1000 to adjust "Other" grouping threshold
min_files = df_lang["files"].sum() / 1000
```

## License

This example is based on the 8Knot project and follows the same principles for data analysis and visualization.

## Related

- [8Knot Project](https://github.com/8Knot/8Knot)
- [Augur Documentation](https://augur.chaoss.io/)
- [Plotly Documentation](https://plotly.com/python/) 