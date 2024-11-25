"""Caching module for storing and retrieving data."""
import json
import pickle
import hashlib
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Union
from functools import wraps
import redis

from src.config.environment import env
from src.utils.logging_config import logger_config

# Get logger
logger = logger_config.get_logger('cache')

class CacheBackend(ABC):
    """Abstract base class for cache backends."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> None:
        """Set value in cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all values from cache."""
        pass

class MemoryCache(CacheBackend):
    """In-memory cache backend."""
    
    def __init__(self):
        """Initialize memory cache."""
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self._cache:
            return None
        
        item = self._cache[key]
        if item['expire'] and time.time() > item['expire']:
            self.delete(key)
            return None
        
        return item['value']
    
    def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> None:
        """Set value in cache."""
        self._cache[key] = {
            'value': value,
            'expire': time.time() + expire if expire else None
        }
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        self._cache.pop(key, None)
    
    def clear(self) -> None:
        """Clear all values from cache."""
        self._cache.clear()

class FileCache(CacheBackend):
    """File-based cache backend."""
    
    def __init__(self):
        """Initialize file cache."""
        self.cache_dir = env.get_path('CACHE_DIR')
        if not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True)
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for key."""
        hashed_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hashed_key}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                item = pickle.load(f)
            
            if item['expire'] and time.time() > item['expire']:
                self.delete(key)
                return None
            
            return item['value']
        except Exception as e:
            logger.error(f"Error reading cache file: {e}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> None:
        """Set value in cache."""
        cache_path = self._get_cache_path(key)
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump({
                    'value': value,
                    'expire': time.time() + expire if expire else None
                }, f)
        except Exception as e:
            logger.error(f"Error writing cache file: {e}")
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
    
    def clear(self) -> None:
        """Clear all values from cache."""
        for cache_file in self.cache_dir.glob('*.cache'):
            cache_file.unlink()

class RedisCache(CacheBackend):
    """Redis cache backend."""
    
    def __init__(self):
        """Initialize Redis cache."""
        self.redis = redis.Redis(
            host=env.get_config('CACHE.HOST'),
            port=env.get_config('CACHE.PORT'),
            password=env.get_config('CACHE.PASSWORD'),
            decode_responses=True
        )
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> None:
        """Set value in cache."""
        try:
            self.redis.set(
                key,
                json.dumps(value),
                ex=expire
            )
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        try:
            self.redis.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
    
    def clear(self) -> None:
        """Clear all values from cache."""
        try:
            self.redis.flushdb()
        except Exception as e:
            logger.error(f"Redis clear error: {e}")

class Cache:
    """Main cache class."""
    
    def __init__(self):
        """Initialize cache with appropriate backend."""
        cache_type = env.get_config('CACHE.TYPE')
        
        if cache_type == 'memory':
            self.backend = MemoryCache()
        elif cache_type == 'redis':
            self.backend = RedisCache()
        else:
            self.backend = FileCache()
        
        self.enabled = env.get_config('CACHE.ENABLED')
        self.default_expire = env.get_config('CACHE.MAX_AGE')
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled:
            return None
        return self.backend.get(key)
    
    def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> None:
        """Set value in cache."""
        if not self.enabled:
            return
        self.backend.set(key, value, expire or self.default_expire)
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        if not self.enabled:
            return
        self.backend.delete(key)
    
    def clear(self) -> None:
        """Clear all values from cache."""
        if not self.enabled:
            return
        self.backend.clear()

def cached(
    prefix: str,
    expire: Optional[int] = None,
    key_func: Optional[callable] = None
):
    """Cache decorator."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not cache.enabled:
                return func(*args, **kwargs)
            
            # Generate cache key
            if key_func:
                key = f"{prefix}:{key_func(*args, **kwargs)}"
            else:
                key_parts = [prefix]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                key = ':'.join(key_parts)
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                logger.debug(f"Cache hit for key: {key}")
                return result
            
            # Call function and cache result
            logger.debug(f"Cache miss for key: {key}")
            result = func(*args, **kwargs)
            cache.set(key, result, expire)
            return result
        
        return wrapper
    return decorator

# Create singleton instance
cache = Cache()
