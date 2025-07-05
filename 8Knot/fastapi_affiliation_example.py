"""
FastAPI Affiliation Endpoints Example

This shows how to create FastAPI endpoints that generate Plotly visualizations
directly without using Celery or cache facade.

Endpoints:
- GET /affiliation/table/{repo_ids} - Returns Plotly table JSON
- GET /affiliation/chart/{repo_ids} - Returns Plotly chart JSON
"""

from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict, Any
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy import create_engine
import os
import logging
from pydantic import BaseModel

# Import the direct query class
from direct_affiliation_example import DirectAffiliationQuery

app = FastAPI(title="8Knot Affiliation API", version="1.0.0")

# Initialize the direct query engine
query_engine = DirectAffiliationQuery()

# Response models
class PlotlyResponse(BaseModel):
    """Response model for Plotly JSON"""
    data: Dict[str, Any]
    success: bool
    message: str
    repo_count: int
    processing_time_seconds: float

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    message: str
    error_type: str

@app.get("/affiliation/table/{repo_ids}", response_model=PlotlyResponse)
async def get_affiliation_table(
    repo_ids: str,
    min_contributions: int = Query(1, ge=1, le=100, description="Minimum contributions to show organization"),
    email_filter: List[str] = Query(None, description="Email domains to exclude (e.g., gmail.com)")
):
    """
    Generate organization affiliation table directly from database.
    
    Args:
        repo_ids: Comma-separated list of repository IDs (e.g., "1,2,3")
        min_contributions: Minimum contributions to include organization
        email_filter: Email domains to exclude from results
        
    Returns:
        Plotly table JSON with organization activity data
    """
    try:
        import time
        start_time = time.time()
        
        # Parse repo IDs
        repo_id_list = [int(x.strip()) for x in repo_ids.split(",")]
        
        if not repo_id_list:
            raise HTTPException(status_code=400, detail="No repository IDs provided")
        
        if len(repo_id_list) > 50:  # Reasonable limit
            raise HTTPException(status_code=400, detail="Too many repositories (max 50)")
        
        # Get Plotly table directly - no caching, no waiting
        table_json = query_engine.create_org_activity_table(repo_id_list, min_contributions)
        
        # Apply email filters if provided
        if email_filter:
            table_json = _apply_email_filter(table_json, email_filter)
        
        processing_time = time.time() - start_time
        
        return PlotlyResponse(
            data=table_json,
            success=True,
            message=f"Table generated for {len(repo_id_list)} repositories",
            repo_count=len(repo_id_list),
            processing_time_seconds=round(processing_time, 2)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid repository IDs: {str(e)}")
    except Exception as e:
        logging.error(f"Error generating affiliation table: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/affiliation/chart/{repo_ids}", response_model=PlotlyResponse)
async def get_affiliation_chart(
    repo_ids: str,
    min_contributions: int = Query(1, ge=1, le=100, description="Minimum contributions to show organization"),
    email_filter: List[str] = Query(None, description="Email domains to exclude (e.g., gmail.com)")
):
    """
    Generate organization affiliation bar chart directly from database.
    
    Args:
        repo_ids: Comma-separated list of repository IDs (e.g., "1,2,3")
        min_contributions: Minimum contributions to include organization
        email_filter: Email domains to exclude from results
        
    Returns:
        Plotly bar chart JSON with organization activity data
    """
    try:
        import time
        start_time = time.time()
        
        # Parse repo IDs
        repo_id_list = [int(x.strip()) for x in repo_ids.split(",")]
        
        if not repo_id_list:
            raise HTTPException(status_code=400, detail="No repository IDs provided")
        
        if len(repo_id_list) > 50:  # Reasonable limit
            raise HTTPException(status_code=400, detail="Too many repositories (max 50)")
        
        # Get Plotly chart directly - no caching, no waiting
        chart_json = query_engine.create_org_activity_chart(repo_id_list, min_contributions)
        
        # Apply email filters if provided
        if email_filter:
            chart_json = _apply_email_filter(chart_json, email_filter)
        
        processing_time = time.time() - start_time
        
        return PlotlyResponse(
            data=chart_json,
            success=True,
            message=f"Chart generated for {len(repo_id_list)} repositories",
            repo_count=len(repo_id_list),
            processing_time_seconds=round(processing_time, 2)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid repository IDs: {str(e)}")
    except Exception as e:
        logging.error(f"Error generating affiliation chart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/affiliation/data/{repo_ids}")
async def get_affiliation_data(
    repo_ids: str,
    format: str = Query("json", description="Response format: json or csv")
):
    """
    Get raw affiliation data directly from database.
    
    Args:
        repo_ids: Comma-separated list of repository IDs
        format: Response format (json or csv)
        
    Returns:
        Raw affiliation data in specified format
    """
    try:
        import time
        start_time = time.time()
        
        # Parse repo IDs
        repo_id_list = [int(x.strip()) for x in repo_ids.split(",")]
        
        if not repo_id_list:
            raise HTTPException(status_code=400, detail="No repository IDs provided")
        
        # Get raw data directly from database
        df = query_engine.get_affiliation_data(repo_id_list)
        
        processing_time = time.time() - start_time
        
        if format.lower() == "csv":
            # Return CSV data
            from fastapi.responses import Response
            csv_data = df.to_csv(index=False)
            return Response(
                content=csv_data,
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=affiliation_data_{len(repo_id_list)}_repos.csv"}
            )
        else:
            # Return JSON data
            return {
                "data": df.to_dict(orient="records"),
                "success": True,
                "message": f"Data retrieved for {len(repo_id_list)} repositories",
                "repo_count": len(repo_id_list),
                "row_count": len(df),
                "processing_time_seconds": round(processing_time, 2)
            }
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid repository IDs: {str(e)}")
    except Exception as e:
        logging.error(f"Error retrieving affiliation data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def _apply_email_filter(plotly_json: Dict[str, Any], email_filter: List[str]) -> Dict[str, Any]:
    """Apply email domain filters to Plotly JSON data"""
    # This is a simplified example - you'd need to implement the actual filtering logic
    # based on the structure of your Plotly JSON data
    
    # For now, just return the original data
    # In a real implementation, you'd filter the data arrays within the Plotly JSON
    return plotly_json

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "8Knot Affiliation API"}

# Example usage and comparison
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "8Knot Affiliation API",
        "version": "1.0.0",
        "description": "Direct database querying without cache facade",
        "features": [
            "Direct SQL queries to Augur database",
            "No Celery background tasks",
            "No PostgreSQL caching layer",
            "Immediate Plotly JSON responses",
            "Raw data export capabilities"
        ],
        "endpoints": {
            "affiliation_table": "/affiliation/table/{repo_ids}",
            "affiliation_chart": "/affiliation/chart/{repo_ids}",
            "affiliation_data": "/affiliation/data/{repo_ids}",
            "health": "/health"
        },
        "example_usage": {
            "table": "/affiliation/table/1,2,3?min_contributions=2",
            "chart": "/affiliation/chart/1,2,3?min_contributions=2&email_filter=gmail.com",
            "data": "/affiliation/data/1,2,3?format=json"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 