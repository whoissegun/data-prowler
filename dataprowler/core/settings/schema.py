"""
Configuration schema for DataProwler.

Defines the validation schema for configuration using Pydantic models.
"""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, HttpUrl, field_validator, AnyHttpUrl, Field

class ApiConfig(BaseModel):
    """API server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    request_timeout: int = 30
    max_content_length: int = 10485760  # 10MB

class GoogleSearchConfig(BaseModel):
    """Google search engine specific configuration."""
    api_key: str = ""
    cx: str = ""
    country: str = "us"

class BingSearchConfig(BaseModel):
    """Bing search engine specific configuration."""
    api_key: str = ""
    country: str = "us"

class SearchConfig(BaseModel):
    """Search engine configuration."""
    engines: List[str] = ["google", "bing"]
    max_results: int = 20
    timeout: int = 10
    google: GoogleSearchConfig = GoogleSearchConfig()
    bing: BingSearchConfig = BingSearchConfig()
    
    @field_validator("engines")
    def validate_engines(cls, v):
        """Validate that specified engines are supported."""
        supported_engines = ["google", "bing", "duckduckgo"]
        for engine in v:
            if engine not in supported_engines:
                raise ValueError(f"Unsupported search engine: {engine}")
        return v

class RetryConfig(BaseModel):
    """Configuration for retry behavior."""
    max_retries: int = 3
    backoff_factor: float = 2.0
    status_forcelist: List[int] = [429, 500, 502, 503, 504]

class ScrollBehaviorConfig(BaseModel):
    """Configuration for scroll behavior during scraping."""
    enabled: bool = True
    max_scrolls: int = 5
    wait_time: float = 1.5

class ScrapingConfig(BaseModel):
    """Web scraping configuration."""
    timeout: int = 30
    retry: RetryConfig = RetryConfig()
    user_agents: List[str] = Field(default_factory=lambda: [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    ])
    respect_robots_txt: bool = True
    javascript_enabled: bool = True
    wait_for_selectors: bool = True
    wait_time: float = 5.0
    scroll_behavior: ScrollBehaviorConfig = ScrollBehaviorConfig()

class AntiBotConfig(BaseModel):
    """Anti-bot detection configuration."""
    use_proxies: bool = False
    proxies: List[str] = []
    rotate_user_agents: bool = True
    mimic_human_behavior: bool = True
    handle_captchas: bool = False
    captcha_service: str = ""
    captcha_api_key: str = ""

class DomainRateLimits(BaseModel):
    """Per-domain rate limits."""
    __root__: Dict[str, int] = {}

class RateLimitingConfig(BaseModel):
    """Rate limiting configuration."""
    enabled: bool = True
    requests_per_minute: int = 10
    domain_specific: Dict[str, int] = Field(default_factory=dict)

class ContentExtractionConfig(BaseModel):
    """ML model configuration for content extraction."""
    model_path: str = ""
    threshold: float = 0.7

class QueryProcessingConfig(BaseModel):
    """ML model configuration for query processing."""
    model_path: str = ""
    max_tokens: int = 1024

class MLConfig(BaseModel):
    """Machine learning configuration."""
    content_extraction: ContentExtractionConfig = ContentExtractionConfig()
    query_processing: QueryProcessingConfig = QueryProcessingConfig()

class DatabaseConfig(BaseModel):
    """Database configuration."""
    url: str = "sqlite:///dataprowler.db"
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False

class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = ""

class RedisConfig(BaseModel):
    """Redis configuration for caching."""
    host: str = "localhost"
    port: int = 6379
    db: int = 0

class FilesystemCacheConfig(BaseModel):
    """Filesystem cache configuration."""
    path: str = ".cache"

class CacheConfig(BaseModel):
    """Caching configuration."""
    enabled: bool = True
    type: str = "memory"
    ttl: int = 3600
    max_size: int = 1000
    redis: RedisConfig = RedisConfig()
    filesystem: FilesystemCacheConfig = FilesystemCacheConfig()
    
    @field_validator("type")
    def validate_cache_type(cls, v):
        """Validate that the cache type is supported."""
        supported_types = ["memory", "redis", "filesystem"]
        if v not in supported_types:
            raise ValueError(f"Unsupported cache type: {v}")
        return v

class PerformanceConfig(BaseModel):
    """Performance tuning configuration."""
    max_workers: int = 4
    timeout: int = 60
    memory_limit: int = 0  # 0 means no limit

class FeaturesConfig(BaseModel):
    """Feature toggle configuration."""
    use_ml_processing: bool = True
    advanced_extraction: bool = True
    site_structure_learning: bool = True

class ConfigSchema(BaseModel):
    """Root configuration schema."""
    api: ApiConfig = ApiConfig()
    search: SearchConfig = SearchConfig()
    scraping: ScrapingConfig = ScrapingConfig()
    anti_bot: AntiBotConfig = AntiBotConfig()
    rate_limiting: RateLimitingConfig = RateLimitingConfig()
    ml: MLConfig = MLConfig()
    database: DatabaseConfig = DatabaseConfig()
    logging: LoggingConfig = LoggingConfig()
    cache: CacheConfig = CacheConfig()
    performance: PerformanceConfig = PerformanceConfig()
    features: FeaturesConfig = FeaturesConfig()