"""Application configuration settings."""

from typing import List, Optional, Union

from pydantic import AnyHttpUrl, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "PRD Generator"
    
    # CORS Settings
    CORS_ORIGINS: Optional[List[str]] = Field(default=None)
    
    # Database Configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "prd_generator"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    def _build_db_connection(self) -> str:
        """Build SQLAlchemy connection string."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
    
    # AI Model Configuration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    DEFAULT_MODEL_PROVIDER: str = "openai"  # Options: openai, anthropic
    
    # Security Settings
    SECRET_KEY: str = "development-secret-key-replace-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Configuration model
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @model_validator(mode='before')
    @classmethod
    def validate_settings(cls, data):
        """Validate and set default settings."""
        # Handle CORS_ORIGINS
        if not data.get('CORS_ORIGINS'):
            data['CORS_ORIGINS'] = ["http://localhost:3000"]
        elif isinstance(data.get('CORS_ORIGINS'), str):
            data['CORS_ORIGINS'] = [origin.strip() for origin in data['CORS_ORIGINS'].split(',') if origin.strip()]
        
        # Handle database URI
        if not data.get('SQLALCHEMY_DATABASE_URI'):
            data['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{data.get('POSTGRES_USER', 'postgres')}:{data.get('POSTGRES_PASSWORD', 'postgres')}@{data.get('POSTGRES_SERVER', 'localhost')}/{data.get('POSTGRES_DB', 'prd_generator')}"
        
        return data


# Create a singleton settings instance
settings = Settings()
