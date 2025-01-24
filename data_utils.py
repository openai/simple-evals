import os
import gzip
import requests
from pathlib import Path

def download_file(url: str, cache_dir: str = "data") -> str:
    """Download a file from URL and cache it locally"""
    # Create cache directory if it doesn't exist
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    
    # Get filename from URL
    filename = url.split("/")[-1]
    cache_path = os.path.join(cache_dir, filename)
    
    # Return cached file if it exists
    if os.path.exists(cache_path):
        return cache_path
        
    # Download file
    response = requests.get(url)
    response.raise_for_status()
    
    # Save to cache
    with open(cache_path, "wb") as f:
        f.write(response.content)
        
    return cache_path
