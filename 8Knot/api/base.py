"""
8Knot API Base Classes
=====================

Base classes for query engines and visualization generators that provide
common functionality and consistent patterns across the API.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sqlalchemy as sa
from sqlalchemy.engine import Engine
import logging
import time
from datetime import datetime

from .config import get_config, get_color_sequence, get_plotly_template
from .utils import DataUtils, FormatUtils, ValidationUtils, ErrorUtils

logger = logging.getLogger(__name__)

class BaseQuery(ABC):
    """Base class for all query engines"""
    
    def __init__(self, engine: Optional[Engine] = None):
        """
        Initialize query engine
        
        Args:
            engine: SQLAlchemy engine (uses config default if None)
        """
        self.config = get_config()
        self.engine = engine or self.config.get_engine()
        self.color_sequence = get_color_sequence()
        
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Execute SQL query and return DataFrame
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            DataFrame with query results
        """
        try:
            start_time = time.time()
            
            with self.engine.connect() as conn:
                if params:
                    result = conn.execute(sa.text(query), params)
                else:
                    result = conn.execute(sa.text(query))
                    
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            execution_time = time.time() - start_time
            logger.info(f"Query executed in {execution_time:.2f}s, returned {len(df)} rows")
            
            return df
            
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise
    
    def validate_repo_ids(self, repo_ids: List[int]) -> bool:
        """Validate repository IDs"""
        return DataUtils.validate_repo_ids(repo_ids) and self.config.validate_repo_ids(repo_ids)
    
    def format_repo_ids_for_sql(self, repo_ids: List[int]) -> str:
        """Format repository IDs for SQL IN clause"""
        return ",".join(str(rid) for rid in repo_ids)
    
    @abstractmethod
    def get_data(self, repo_ids: List[int], **kwargs) -> pd.DataFrame:
        """
        Get data for the specified repositories
        
        Args:
            repo_ids: List of repository IDs
            **kwargs: Additional parameters
            
        Returns:
            DataFrame with query results
        """
        pass
    
    def create_response(self, data: Any, success: bool = True, message: str = "", 
                       processing_time: float = 0.0, **kwargs) -> Dict[str, Any]:
        """Create standardized API response"""
        response = {
            "success": success,
            "data": data,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "processing_time_seconds": round(processing_time, 3)
        }
        response.update(kwargs)
        return response

class BaseVisualization(ABC):
    """Base class for all visualization generators"""
    
    def __init__(self, query_engine: Optional[BaseQuery] = None):
        """
        Initialize visualization generator
        
        Args:
            query_engine: Query engine instance
        """
        self.config = get_config()
        self.query_engine = query_engine
        self.color_sequence = get_color_sequence()
        self.template = get_plotly_template()
        
    def apply_template(self, fig: go.Figure) -> go.Figure:
        """Apply 8Knot template to figure"""
        fig.update_layout(self.template["layout"])
        return fig
    
    def create_no_data_figure(self, title: str = "No Data Available", 
                            message: str = "No data found for the selected criteria") -> go.Figure:
        """Create figure for no data scenario"""
        fig = go.Figure()
        fig.update_layout(
            title=title,
            annotations=[{
                'text': message,
                'showarrow': False,
                'x': 0.5,
                'y': 0.5,
                'xref': 'paper',
                'yref': 'paper',
                'font': {'size': 16}
            }]
        )
        return self.apply_template(fig)
    
    def create_error_figure(self, title: str = "Error", 
                          message: str = "An error occurred while generating the visualization") -> go.Figure:
        """Create figure for error scenario"""
        fig = go.Figure()
        fig.update_layout(
            title=title,
            annotations=[{
                'text': message,
                'showarrow': False,
                'x': 0.5,
                'y': 0.5,
                'xref': 'paper',
                'yref': 'paper',
                'font': {'size': 16, 'color': 'red'}
            }]
        )
        return self.apply_template(fig)
    
    @abstractmethod
    def create_figure(self, df: pd.DataFrame, **kwargs) -> go.Figure:
        """
        Create Plotly figure from data
        
        Args:
            df: DataFrame with data
            **kwargs: Additional parameters
            
        Returns:
            Plotly figure
        """
        pass
    
    def generate_visualization(self, repo_ids: List[int], **kwargs) -> Dict[str, Any]:
        """
        Generate complete visualization with data fetching and error handling
        
        Args:
            repo_ids: List of repository IDs
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with Plotly figure JSON and metadata
        """
        try:
            start_time = time.time()
            
            # Validate inputs
            if not DataUtils.validate_repo_ids(repo_ids):
                return ErrorUtils.create_error_response("Invalid repository IDs")
            
            # Get data
            if not self.query_engine:
                return ErrorUtils.create_error_response("No query engine configured")
                
            df = self.query_engine.get_data(repo_ids, **kwargs)
            
            # Create figure
            if df.empty:
                fig = self.create_no_data_figure()
            else:
                fig = self.create_figure(df, **kwargs)
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "data": fig.to_dict(),
                "message": f"Visualization generated for {len(repo_ids)} repositories",
                "repo_count": len(repo_ids),
                "data_points": len(df),
                "processing_time_seconds": round(processing_time, 3),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Visualization generation failed: {str(e)}")
            return ErrorUtils.create_error_response(f"Visualization generation failed: {str(e)}")

class BaseMetric(ABC):
    """Base class for simple metrics"""
    
    def __init__(self, query_engine: Optional[BaseQuery] = None):
        """
        Initialize metric calculator
        
        Args:
            query_engine: Query engine instance
        """
        self.config = get_config()
        self.query_engine = query_engine
        
    @abstractmethod
    def calculate(self, repo_ids: List[int], **kwargs) -> Union[int, float, str]:
        """
        Calculate metric value
        
        Args:
            repo_ids: List of repository IDs
            **kwargs: Additional parameters
            
        Returns:
            Metric value
        """
        pass
    
    def get_metric(self, repo_ids: List[int], **kwargs) -> Dict[str, Any]:
        """
        Get metric with error handling and formatting
        
        Args:
            repo_ids: List of repository IDs
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with metric value and metadata
        """
        try:
            start_time = time.time()
            
            # Validate inputs
            if not DataUtils.validate_repo_ids(repo_ids):
                return ErrorUtils.create_error_response("Invalid repository IDs")
            
            # Calculate metric
            value = self.calculate(repo_ids, **kwargs)
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "value": value,
                "formatted_value": FormatUtils.format_number(value) if isinstance(value, (int, float)) else str(value),
                "repo_count": len(repo_ids),
                "processing_time_seconds": round(processing_time, 3),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Metric calculation failed: {str(e)}")
            return ErrorUtils.create_error_response(f"Metric calculation failed: {str(e)}")

class BaseTable(BaseVisualization):
    """Base class for table visualizations"""
    
    def create_table_figure(self, df: pd.DataFrame, columns: List[str], 
                          title: str = "Data Table") -> go.Figure:
        """Create Plotly table figure"""
        if df.empty:
            return self.create_no_data_figure(title)
        
        # Format data for table
        table_data = []
        for col in columns:
            if col in df.columns:
                table_data.append(df[col].tolist())
            else:
                table_data.append([""] * len(df))
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=columns,
                fill_color='paleturquoise',
                align='left',
                font=dict(size=12, color='black')
            ),
            cells=dict(
                values=table_data,
                fill_color='lightcyan',
                align='left',
                font=dict(size=11, color='black')
            )
        )])
        
        fig.update_layout(title=title, height=400)
        return self.apply_template(fig)

class BaseChart(BaseVisualization):
    """Base class for chart visualizations"""
    
    def create_bar_chart(self, df: pd.DataFrame, x_col: str, y_col: str, 
                        title: str = "Bar Chart", **kwargs) -> go.Figure:
        """Create bar chart"""
        if df.empty:
            return self.create_no_data_figure(title)
        
        fig = px.bar(
            df, 
            x=x_col, 
            y=y_col, 
            title=title,
            color_discrete_sequence=self.color_sequence,
            **kwargs
        )
        return self.apply_template(fig)
    
    def create_line_chart(self, df: pd.DataFrame, x_col: str, y_col: str, 
                         title: str = "Line Chart", **kwargs) -> go.Figure:
        """Create line chart"""
        if df.empty:
            return self.create_no_data_figure(title)
        
        fig = px.line(
            df, 
            x=x_col, 
            y=y_col, 
            title=title,
            color_discrete_sequence=self.color_sequence,
            **kwargs
        )
        return self.apply_template(fig)
    
    def create_pie_chart(self, df: pd.DataFrame, values_col: str, names_col: str, 
                        title: str = "Pie Chart", **kwargs) -> go.Figure:
        """Create pie chart"""
        if df.empty:
            return self.create_no_data_figure(title)
        
        fig = px.pie(
            df, 
            values=values_col, 
            names=names_col, 
            title=title,
            color_discrete_sequence=self.color_sequence,
            **kwargs
        )
        return self.apply_template(fig)
    
    def create_scatter_plot(self, df: pd.DataFrame, x_col: str, y_col: str, 
                           title: str = "Scatter Plot", **kwargs) -> go.Figure:
        """Create scatter plot"""
        if df.empty:
            return self.create_no_data_figure(title)
        
        fig = px.scatter(
            df, 
            x=x_col, 
            y=y_col, 
            title=title,
            color_discrete_sequence=self.color_sequence,
            **kwargs
        )
        return self.apply_template(fig) 