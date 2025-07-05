"""
8Knot API Configuration
======================

Configuration management for the 8Knot API including database connections,
styling, and visualization settings.
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import sqlalchemy as sa
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    host: str = os.getenv('AUGUR_HOST', 'localhost')
    port: int = int(os.getenv('AUGUR_PORT', '5432'))
    database: str = os.getenv('AUGUR_DATABASE', 'augur')
    username: str = os.getenv('AUGUR_USERNAME', 'augur')
    password: str = os.getenv('AUGUR_PASSWORD', 'augur')
    pool_size: int = int(os.getenv('AUGUR_POOL_SIZE', '5'))
    max_overflow: int = int(os.getenv('AUGUR_MAX_OVERFLOW', '10'))
    pool_timeout: int = int(os.getenv('AUGUR_POOL_TIMEOUT', '30'))
    
    @property
    def connection_string(self) -> str:
        """Generate SQLAlchemy connection string"""
        return f"postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

@dataclass
class StyleConfig:
    """Styling configuration for visualizations"""
    
    # 8Knot color palette
    color_sequence: List[str] = field(default_factory=lambda: [
        "#B5B682",  # sage
        "#c0bc5d",  # citron (yellow-ish)
        "#6C8975",  # reseda green
        "#D9AE8E",  # buff (pale pink)
        "#FFBF51",  # xanthous (orange-ish)
        "#C7A5A5",  # rosy brown
    ])
    
    # Dark theme colors
    background_color: str = "#1e1e1e"
    text_color: str = "#ffffff"
    grid_color: str = "#3e3e3e"
    
    # Font settings
    font_family: str = "Arial, sans-serif"
    font_size: int = 14
    title_font_size: int = 18
    
    # Chart margins
    margin_left: int = 60
    margin_right: int = 60
    margin_top: int = 80
    margin_bottom: int = 60
    
    # Default chart dimensions
    default_width: int = 800
    default_height: int = 600

@dataclass
class APIConfig:
    """Main API configuration class"""
    
    # Database configuration
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    
    # Styling configuration
    style: StyleConfig = field(default_factory=StyleConfig)
    
    # API settings
    max_repositories: int = int(os.getenv('MAX_REPOSITORIES', '50'))
    default_page_size: int = int(os.getenv('DEFAULT_PAGE_SIZE', '100'))
    query_timeout: int = int(os.getenv('QUERY_TIMEOUT', '30'))
    
    # Caching settings
    enable_caching: bool = os.getenv('ENABLE_CACHING', 'true').lower() == 'true'
    cache_ttl: int = int(os.getenv('CACHE_TTL', '300'))  # 5 minutes
    
    # Validation settings
    validate_repo_ids: bool = os.getenv('VALIDATE_REPO_IDS', 'true').lower() == 'true'
    
    # Private attributes
    _engine: Optional[Engine] = field(default=None, init=False, repr=False)
    _session_factory: Optional[sessionmaker] = field(default=None, init=False, repr=False)
    
    def get_engine(self) -> Engine:
        """Get or create database engine"""
        if self._engine is None:
            self._engine = sa.create_engine(
                self.database.connection_string,
                pool_size=self.database.pool_size,
                max_overflow=self.database.max_overflow,
                pool_timeout=self.database.pool_timeout,
                echo=False  # Set to True for SQL debugging
            )
            logger.info(f"Created database engine for {self.database.host}:{self.database.port}")
        return self._engine
    
    def get_session_factory(self) -> sessionmaker:
        """Get or create session factory"""
        if self._session_factory is None:
            self._session_factory = sessionmaker(bind=self.get_engine())
        return self._session_factory
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            engine = self.get_engine()
            with engine.connect() as conn:
                conn.execute(sa.text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_plotly_template(self) -> Dict[str, Any]:
        """Get Plotly template configuration"""
        return {
            "layout": {
                "font": {
                    "family": self.style.font_family,
                    "size": self.style.font_size,
                    "color": self.style.text_color
                },
                "title": {
                    "font": {
                        "size": self.style.title_font_size,
                        "color": self.style.text_color
                    },
                    "x": 0.5,
                    "xanchor": "center"
                },
                "paper_bgcolor": self.style.background_color,
                "plot_bgcolor": self.style.background_color,
                "colorway": self.style.color_sequence,
                "xaxis": {
                    "gridcolor": self.style.grid_color,
                    "color": self.style.text_color
                },
                "yaxis": {
                    "gridcolor": self.style.grid_color,
                    "color": self.style.text_color
                },
                "margin": {
                    "l": self.style.margin_left,
                    "r": self.style.margin_right,
                    "t": self.style.margin_top,
                    "b": self.style.margin_bottom
                },
                "width": self.style.default_width,
                "height": self.style.default_height
            }
        }
    
    def validate_repo_ids(self, repo_ids: List[int]) -> bool:
        """Validate repository IDs against database"""
        if not self.validate_repo_ids:
            return True
            
        try:
            engine = self.get_engine()
            with engine.connect() as conn:
                query = sa.text("""
                    SELECT COUNT(*) as count
                    FROM augur_data.repo
                    WHERE repo_id = ANY(:repo_ids)
                """)
                result = conn.execute(query, {"repo_ids": repo_ids})
                found_count = result.scalar()
                return found_count == len(repo_ids)
        except Exception as e:
            logger.error(f"Error validating repository IDs: {e}")
            return False

# Global configuration instance
config = APIConfig()

# Convenience functions
def get_config() -> APIConfig:
    """Get the global configuration instance"""
    return config

def get_engine() -> Engine:
    """Get the database engine"""
    return config.get_engine()

def get_color_sequence() -> List[str]:
    """Get the 8Knot color sequence"""
    return config.style.color_sequence

def get_plotly_template() -> Dict[str, Any]:
    """Get the Plotly template"""
    return config.get_plotly_template() 