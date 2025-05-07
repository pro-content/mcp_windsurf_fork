#!/usr/bin/env python3
"""
Filesystem MCP Server

This server provides tools for interacting with the local filesystem through MCP.
It supports reading files, listing directories, searching files, and monitoring file changes.
"""

import os
import re
import glob
import logging
import json
from pathlib import Path
from typing import List, Dict, Optional, Union, Any

from mcp.server.fastmcp import FastMCP, Context

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create the MCP server
mcp = FastMCP("Filesystem")

# Security: Define a base directory to restrict access
# Default to current directory if not specified
BASE_DIR = os.getenv("MCP_BASE_DIR", os.getcwd())
logger.info(f"Base directory set to: {BASE_DIR}")

def secure_path(path: str) -> str:
    """
    Ensure the path is within the allowed base directory to prevent directory traversal attacks.
    
    Args:
        path: The requested file or directory path
        
    Returns:
        The absolute path, restricted to the base directory
    """
    # Convert to absolute path
    if not os.path.isabs(path):
        path = os.path.join(BASE_DIR, path)
    
    # Normalize to resolve any '..' components
    normalized_path = os.path.normpath(path)
    
    # Ensure the path is within the base directory
    if not normalized_path.startswith(BASE_DIR):
        logger.warning(f"Attempted access outside base directory: {path}")
        raise ValueError(f"Access denied: Path must be within {BASE_DIR}")
    
    return normalized_path

@mcp.tool()
def read_file(path: str, ctx: Context) -> str:
    """
    Read and return the contents of a file.
    
    This tool reads the contents of a file at the specified path and returns them as a string.
    The path can be absolute or relative to the base directory.
    
    Args:
        path: The path to the file to read
        ctx: The MCP context
        
    Returns:
        The contents of the file as a string
        
    Raises:
        ValueError: If the file does not exist or cannot be read
    """
    logger.debug(f"Attempting to read file at path: {path}")
    try:
        secure_file_path = secure_path(path)
        
        # Check if file exists
        if not os.path.isfile(secure_file_path):
            logger.error(f"File does not exist: {secure_file_path}")
            raise ValueError(f"File does not exist: {path}")
        
        # Read file content
        with open(secure_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        logger.debug(f"Successfully read file at path: {path}")
        return content
    
    except Exception as e:
        logger.error(f"Error reading file at path: {path} - {e}")
        raise ValueError(f"Failed to read file: {str(e)}")

@mcp.tool()
def list_directory(path: str, include_hidden: bool = False) -> List[Dict[str, Any]]:
    """
    List the contents of a directory.
    
    This tool lists all files and subdirectories in the specified directory.
    The path can be absolute or relative to the base directory.
    
    Args:
        path: The path to the directory to list
        include_hidden: Whether to include hidden files (starting with '.')
        
    Returns:
        A list of dictionaries containing information about each item:
        - name: The name of the file or directory
        - type: 'file' or 'directory'
        - size: The size in bytes (for files only)
        - is_hidden: Whether the item is hidden
        
    Raises:
        ValueError: If the directory does not exist or cannot be accessed
    """
    logger.debug(f"Attempting to list directory at path: {path}")
    try:
        secure_dir_path = secure_path(path)
        
        # Check if directory exists
        if not os.path.isdir(secure_dir_path):
            logger.error(f"Directory does not exist: {secure_dir_path}")
            raise ValueError(f"Directory does not exist: {path}")
        
        # List directory contents
        items = []
        for item in os.listdir(secure_dir_path):
            # Skip hidden files if not included
            if not include_hidden and item.startswith('.'):
                continue
                
            item_path = os.path.join(secure_dir_path, item)
            is_dir = os.path.isdir(item_path)
            
            item_info = {
                "name": item,
                "type": "directory" if is_dir else "file",
                "is_hidden": item.startswith('.')
            }
            
            # Add size for files
            if not is_dir:
                item_info["size"] = os.path.getsize(item_path)
                
            items.append(item_info)
        
        logger.debug(f"Successfully listed directory at path: {path}")
        return items
    
    except Exception as e:
        logger.error(f"Error listing directory at path: {path} - {e}")
        raise ValueError(f"Failed to list directory: {str(e)}")

@mcp.tool()
def search_files(
    pattern: str, 
    search_path: str = ".", 
    recursive: bool = True, 
    content_regex: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search for files matching a pattern and optionally containing specific content.
    
    This tool searches for files matching a glob pattern and optionally containing 
    text matching a regular expression.
    
    Args:
        pattern: The glob pattern to match filenames (e.g., "*.py", "data/*.csv")
        search_path: The directory to search in (default: current directory)
        recursive: Whether to search recursively in subdirectories
        content_regex: Optional regex pattern to search within file contents
        
    Returns:
        A list of dictionaries containing information about matching files:
        - path: The relative path to the file
        - size: The size in bytes
        - matches: List of matching lines (only if content_regex is provided)
        
    Raises:
        ValueError: If the search path does not exist or the pattern is invalid
    """
    logger.debug(f"Searching for files matching pattern: {pattern} in {search_path}")
    try:
        secure_search_path = secure_path(search_path)
        
        # Check if search path exists
        if not os.path.isdir(secure_search_path):
            logger.error(f"Search path does not exist: {secure_search_path}")
            raise ValueError(f"Search path does not exist: {search_path}")
        
        # Prepare the glob pattern
        if recursive:
            search_pattern = os.path.join(secure_search_path, "**", pattern)
        else:
            search_pattern = os.path.join(secure_search_path, pattern)
        
        # Find matching files
        matching_files = []
        for file_path in glob.glob(search_pattern, recursive=recursive):
            if os.path.isfile(file_path):
                result = {
                    "path": os.path.relpath(file_path, BASE_DIR),
                    "size": os.path.getsize(file_path)
                }
                
                # If content regex is provided, search within the file
                if content_regex:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Find all matches in the content
                        regex = re.compile(content_regex)
                        matches = []
                        
                        for i, line in enumerate(content.splitlines()):
                            if regex.search(line):
                                matches.append({
                                    "line_number": i + 1,
                                    "content": line.strip()
                                })
                        
                        if matches:
                            result["matches"] = matches
                            matching_files.append(result)
                    except Exception as e:
                        logger.warning(f"Could not search content in {file_path}: {e}")
                else:
                    matching_files.append(result)
        
        logger.debug(f"Found {len(matching_files)} matching files")
        return matching_files
    
    except Exception as e:
        logger.error(f"Error searching files: {e}")
        raise ValueError(f"Failed to search files: {str(e)}")

# Optional: File monitoring resource
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    
    # Store file changes
    file_changes = []
    
    class ChangeHandler(FileSystemEventHandler):
        def on_any_event(self, event):
            if event.is_directory:
                return
            
            # Record the change
            change = {
                "path": os.path.relpath(event.src_path, BASE_DIR),
                "type": event.event_type,
                "time": os.path.getmtime(event.src_path) if os.path.exists(event.src_path) else None
            }
            file_changes.append(change)
            
            # Keep only the last 100 changes
            if len(file_changes) > 100:
                file_changes.pop(0)
    
    # Set up the observer
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, BASE_DIR, recursive=True)
    observer.start()
    logger.info("File monitoring enabled")
    
    @mcp.resource("file-changes://recent")
    def get_recent_changes() -> str:
        """
        Get a list of recent file changes.
        
        This resource returns information about recent file changes that have been
        monitored by the server.
        
        Returns:
            A JSON string containing recent file changes
        """
        return json.dumps(file_changes)
    
except ImportError:
    logger.info("File monitoring disabled (watchdog not installed)")

if __name__ == "__main__":
    logger.info("Starting Filesystem MCP Server")
    mcp.run()
