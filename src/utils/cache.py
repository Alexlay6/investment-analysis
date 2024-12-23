import streamlit as st
from functools import wraps
from datetime import datetime, timedelta
import hashlib
import json
import pickle
from typing import Any, Callable, Dict, Optional

class CacheManager:
    """Manage caching of financial data and analysis results."""
    
    @staticmethod
    def hash_params(*args, **kwargs) -> str:
        """Create a hash of function parameters."""
        param_str = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)
        return hashlib.md5(param_str.encode()).hexdigest()

    @staticmethod
    def cache_data(ttl_seconds: int = 3600):
        """Cache decorator with time-to-live."""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Create cache key
                cache_key = f"{func.__name__}_{CacheManager.hash_params(*args, **kwargs)}"
                
                # Check cache
                if cache_key in st.session_state:
                    cached_data = st.session_state[cache_key]
                    if datetime.now() < cached_data['expiry']:
                        return cached_data['data']
                
                # Get fresh data
                data = func(*args, **kwargs)
                
                # Cache the result
                st.session_state[cache_key] = {
                    'data': data,
                    'expiry': datetime.now() + timedelta(seconds=ttl_seconds)
                }
                
                return data
            return wrapper
        return decorator

    @staticmethod
    def clear_cache(pattern: Optional[str] = None):
        """Clear cached data matching pattern."""
        if pattern:
            keys_to_clear = [
                key for key in st.session_state.keys()
                if pattern in key
            ]
        else:
            keys_to_clear = list(st.session_state.keys())
            
        for key in keys_to_clear:
            del st.session_state[key]

# Cache decorators
def cache_market_data(func):
    """Cache market data for 1 hour."""
    return CacheManager.cache_data(ttl_seconds=3600)(func)

def cache_financial_data(func):
    """Cache financial data for 24 hours."""
    return CacheManager.cache_data(ttl_seconds=86400)(func)

def cache_analysis(func):
    """Cache analysis results for 4 hours."""
    return CacheManager.cache_data(ttl_seconds=14400)(func)