"""
8Knot API Utilities
==================

Utility functions for common patterns used across the API including date handling,
formatting, data processing, and validation.
"""

import datetime as dt
from typing import List, Dict, Any, Optional, Union, Tuple
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
import logging

logger = logging.getLogger(__name__)

class DateUtils:
    """Utility class for date and time operations"""
    
    @staticmethod
    def get_graph_time_values(interval: Union[str, int]) -> Tuple[Optional[List[str]], str, str, Union[str, int]]:
        """
        Convert interval to Plotly figure update values.
        
        Args:
            interval: How long between time bins (D, W, M, M3, M6, M12, or milliseconds)
            
        Returns:
            Tuple of (x_range, x_name, hover_template, period)
        """
        today = dt.date.today()
        x_r = None
        x_name = "Year"
        hover = "Year: %{x|%Y}"
        period = "M12"

        # Convert interval to standard format
        if interval == 86400000 or interval == "D":  # Days
            x_r = [str(today - dt.timedelta(weeks=4)), str(today)]
            x_name = "Day"
            hover = "Day: %{x|%b %d, %Y}"
            period = 86400000 * 2
        elif interval == 604800000 or interval == "W":  # Weeks
            x_r = [str(today - dt.timedelta(weeks=30)), str(today)]
            x_name = "Week"
            hover = "Week: %{x|%b %d, %Y}"
            period = 1814400000
        elif interval == "M" or interval == "M1":  # Months
            x_r = [str(today - dt.timedelta(weeks=104)), str(today)]
            x_name = "Month"
            hover = "Month: %{x|%b %Y}"
            period = "M3"
        elif interval == "M3":  # Quarters
            x_r = [str(today - dt.timedelta(weeks=312)), str(today)]
            x_name = "Quarter"
            hover = "Quarter: %{x}"
            period = "M6"
        elif interval == "M6":  # Half years
            x_r = [str(today - dt.timedelta(weeks=624)), str(today)]
            x_name = "Semiannual"
            hover = "Semiannual: %{x}"
            period = "M12"
        else:  # Default to years
            period = "M12"

        return x_r, x_name, hover, period
    
    @staticmethod
    def format_date_range(start_date: dt.date, end_date: dt.date) -> str:
        """Format date range for display"""
        return f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"
    
    @staticmethod
    def get_date_bins(start_date: dt.date, end_date: dt.date, interval: str) -> List[dt.date]:
        """Generate date bins for time series data"""
        bins = []
        current_date = start_date
        
        while current_date <= end_date:
            bins.append(current_date)
            if interval == "D":
                current_date += dt.timedelta(days=1)
            elif interval == "W":
                current_date += dt.timedelta(weeks=1)
            elif interval in ["M", "M1"]:
                current_date += relativedelta(months=1)
            elif interval == "M3":
                current_date += relativedelta(months=3)
            elif interval == "M6":
                current_date += relativedelta(months=6)
            elif interval == "M12":
                current_date += relativedelta(months=12)
            else:
                current_date += relativedelta(months=1)
        
        return bins

class FormatUtils:
    """Utility class for formatting data"""
    
    @staticmethod
    def format_number(value: Union[int, float], precision: int = 2) -> str:
        """Format numbers with appropriate precision and units"""
        if pd.isna(value):
            return "N/A"
            
        if isinstance(value, (int, float)):
            if value >= 1_000_000:
                return f"{value / 1_000_000:.{precision}f}M"
            elif value >= 1_000:
                return f"{value / 1_000:.{precision}f}K"
            else:
                return f"{value:.{precision}f}".rstrip('0').rstrip('.')
        
        return str(value)
    
    @staticmethod
    def format_percentage(value: float, precision: int = 1) -> str:
        """Format percentage values"""
        if pd.isna(value):
            return "N/A"
        return f"{value:.{precision}f}%"
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format duration in seconds to human readable format"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}d {hours}h"
    
    @staticmethod
    def clean_string(value: str) -> str:
        """Clean string values for display"""
        if pd.isna(value) or value is None:
            return ""
        return str(value).strip()
    
    @staticmethod
    def truncate_string(value: str, max_length: int = 50) -> str:
        """Truncate string to maximum length"""
        if len(value) <= max_length:
            return value
        return value[:max_length-3] + "..."

class DataUtils:
    """Utility class for data processing"""
    
    @staticmethod
    def validate_repo_ids(repo_ids: List[int]) -> bool:
        """Validate repository IDs"""
        if not repo_ids:
            return False
        
        # Check if all are integers
        if not all(isinstance(rid, int) for rid in repo_ids):
            return False
            
        # Check if all are positive
        if not all(rid > 0 for rid in repo_ids):
            return False
            
        return True
    
    @staticmethod
    def parse_repo_ids(repo_ids_str: str) -> List[int]:
        """Parse repository IDs from string"""
        try:
            return [int(x.strip()) for x in repo_ids_str.split(",") if x.strip()]
        except (ValueError, AttributeError):
            return []
    
    @staticmethod
    def safe_divide(numerator: float, denominator: float) -> float:
        """Safe division that handles zero division"""
        if denominator == 0:
            return 0.0
        return numerator / denominator
    
    @staticmethod
    def calculate_percentage(part: float, total: float) -> float:
        """Calculate percentage with safe division"""
        if total == 0:
            return 0.0
        return (part / total) * 100
    
    @staticmethod
    def group_small_values(df: pd.DataFrame, value_col: str, label_col: str, 
                          threshold: float = 0.01, other_label: str = "Other") -> pd.DataFrame:
        """Group small values into 'Other' category"""
        if df.empty:
            return df
            
        # Calculate total
        total = df[value_col].sum()
        
        # Calculate percentages
        df_copy = df.copy()
        df_copy['percentage'] = df_copy[value_col] / total
        
        # Split into main and other
        main_df = df_copy[df_copy['percentage'] >= threshold]
        other_df = df_copy[df_copy['percentage'] < threshold]
        
        # If there are small values, group them
        if not other_df.empty:
            other_row = pd.DataFrame({
                label_col: [other_label],
                value_col: [other_df[value_col].sum()],
                'percentage': [other_df['percentage'].sum()]
            })
            main_df = pd.concat([main_df, other_row], ignore_index=True)
        
        return main_df.drop('percentage', axis=1)
    
    @staticmethod
    def handle_null_values(df: pd.DataFrame, strategy: str = "drop") -> pd.DataFrame:
        """Handle null values in dataframe"""
        if strategy == "drop":
            return df.dropna()
        elif strategy == "fill_zero":
            return df.fillna(0)
        elif strategy == "fill_mean":
            return df.fillna(df.mean())
        else:
            return df
    
    @staticmethod
    def sort_by_value(df: pd.DataFrame, value_col: str, ascending: bool = False) -> pd.DataFrame:
        """Sort dataframe by value column"""
        return df.sort_values(value_col, ascending=ascending)

class ValidationUtils:
    """Utility class for validation"""
    
    @staticmethod
    def validate_date_range(start_date: dt.date, end_date: dt.date) -> bool:
        """Validate date range"""
        if start_date > end_date:
            return False
        
        # Check if date range is reasonable (not more than 10 years)
        if (end_date - start_date).days > 3650:
            return False
            
        return True
    
    @staticmethod
    def validate_interval(interval: str) -> bool:
        """Validate time interval"""
        valid_intervals = ["D", "W", "M", "M1", "M3", "M6", "M12"]
        return interval in valid_intervals
    
    @staticmethod
    def validate_limit(limit: int, max_limit: int = 1000) -> bool:
        """Validate limit parameter"""
        return 1 <= limit <= max_limit
    
    @staticmethod
    def validate_parameters(params: Dict[str, Any], required: List[str]) -> List[str]:
        """Validate required parameters"""
        missing = []
        for param in required:
            if param not in params or params[param] is None:
                missing.append(param)
        return missing

class ErrorUtils:
    """Utility class for error handling"""
    
    @staticmethod
    def create_error_response(message: str, error_type: str = "ValidationError") -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "success": False,
            "error": {
                "type": error_type,
                "message": message,
                "timestamp": dt.datetime.now().isoformat()
            }
        }
    
    @staticmethod
    def log_error(error: Exception, context: str = "") -> None:
        """Log error with context"""
        logger.error(f"Error in {context}: {str(error)}", exc_info=True)
    
    @staticmethod
    def create_no_data_response(message: str = "No data available") -> Dict[str, Any]:
        """Create response for no data scenarios"""
        return {
            "success": True,
            "data": None,
            "message": message,
            "timestamp": dt.datetime.now().isoformat()
        }

# Convenience functions for common operations
def format_repo_ids(repo_ids: List[int]) -> str:
    """Format repository IDs for SQL IN clause"""
    return ",".join(str(rid) for rid in repo_ids)

def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return dt.datetime.now().isoformat()

def calculate_age_in_days(start_date: dt.date, end_date: Optional[dt.date] = None) -> int:
    """Calculate age in days"""
    if end_date is None:
        end_date = dt.date.today()
    return (end_date - start_date).days 