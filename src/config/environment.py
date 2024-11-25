"""Environment configuration module."""
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Environment:
    """Environment configuration class."""
    
    def __init__(self):
        """Initialize environment configuration."""
        self.env = os.getenv('APP_ENV', 'development')
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.setup_paths()
        self.load_config()
    
    def setup_paths(self) -> None:
        """Setup directory paths based on environment."""
        # Base directories
        self.paths = {
            'BASE_DIR': self.base_dir,
            'DATA_DIR': self.base_dir / 'data',
            'CACHE_DIR': self.base_dir / 'data' / 'cache',
            'LOG_DIR': self.base_dir / 'logs',
            'TEMP_DIR': self.base_dir / 'temp',
            'CONFIG_DIR': self.base_dir / 'config'
        }
        
        # Create directories if they don't exist
        for path in self.paths.values():
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
    
    def load_config(self) -> None:
        """Load configuration based on environment."""
        self.config = {
            'DEBUG': self.env != 'production',
            'TESTING': self.env == 'testing',
            'API_VERSION': 'v1',
            'LOG_LEVEL': 'DEBUG' if self.env != 'production' else 'INFO',
            
            # API Configuration
            'API': {
                'ZILLOW_API_KEY': os.getenv('RAPIDAPI_ZILLOW_API_KEY'),
                'ZILLOW_API_HOST': 'zillow-com1.p.rapidapi.com',
                'ZILLOW_BASE_URL': 'https://zillow-com1.p.rapidapi.com',
                'TIMEOUT': 30,
                'RETRY_ATTEMPTS': 3,
                'RETRY_BACKOFF': 2
            },
            
            # Cache Configuration
            'CACHE': {
                'ENABLED': True,
                'TYPE': 'filesystem',
                'MAX_AGE': 3600,
                'MAX_SIZE': 1000,
                'COMPRESSION': True
            },
            
            # Database Configuration (if needed)
            'DATABASE': {
                'TYPE': 'sqlite',
                'NAME': 'real_estate.db',
                'HOST': None,
                'PORT': None,
                'USER': None,
                'PASSWORD': None
            },
            
            # Logging Configuration
            'LOGGING': {
                'FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'DATE_FORMAT': '%Y-%m-%d %H:%M:%S',
                'BACKUP_COUNT': 5,
                'MAX_BYTES': 10485760  # 10MB
            },
            
            # File Storage Configuration
            'STORAGE': {
                'TYPE': 'local',
                'COMPRESS_IMAGES': True,
                'MAX_IMAGE_SIZE': 2097152,  # 2MB
                'ALLOWED_EXTENSIONS': ['jpg', 'jpeg', 'png', 'gif']
            }
        }
        
        # Environment-specific overrides
        if self.env == 'development':
            self.config.update({
                'CACHE': {
                    'ENABLED': True,
                    'TYPE': 'memory',
                    'MAX_AGE': 300,  # 5 minutes
                    'MAX_SIZE': 100
                }
            })
        
        elif self.env == 'testing':
            self.config.update({
                'CACHE': {
                    'ENABLED': False
                },
                'DATABASE': {
                    'NAME': 'test_real_estate.db'
                }
            })
        
        elif self.env == 'production':
            self.config.update({
                'CACHE': {
                    'ENABLED': True,
                    'TYPE': 'redis',
                    'HOST': os.getenv('REDIS_HOST', 'localhost'),
                    'PORT': int(os.getenv('REDIS_PORT', 6379)),
                    'PASSWORD': os.getenv('REDIS_PASSWORD')
                }
            })
    
    def get_path(self, name: str) -> Path:
        """Get path by name."""
        return self.paths.get(name.upper())
    
    def get_config(self, key: str = None) -> Any:
        """Get configuration value by key."""
        if key is None:
            return self.config
        
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k)
            if value is None:
                return None
        return value
    
    @property
    def is_development(self) -> bool:
        """Check if environment is development."""
        return self.env == 'development'
    
    @property
    def is_testing(self) -> bool:
        """Check if environment is testing."""
        return self.env == 'testing'
    
    @property
    def is_production(self) -> bool:
        """Check if environment is production."""
        return self.env == 'production'

# Create singleton instance
env = Environment()
