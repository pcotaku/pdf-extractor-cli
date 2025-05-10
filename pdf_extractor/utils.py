"""
Utility functions for the PDF Extractor CLI
"""
import os
import logging
import re
from typing import List, Tuple, Set


def setup_logging(log_level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging configuration
    
    Args:
        log_level: The logging level to use
        
    Returns:
        A configured logger object
    """
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logger = logging.getLogger("pdf_extractor")
    return logger


def ensure_output_dir(dirname: str = "output") -> str:
    """
    Ensure the output directory exists, creating it if necessary
    
    Args:
        dirname: Name of the directory to create
        
    Returns:
        Path to the output directory
    """
    os.makedirs(dirname, exist_ok=True)
    return dirname


def parse_page_ranges(pages_str: str) -> Set[int]:
    """
    Parse a string like "1-3,5,7-9" into a set of page numbers
    
    Args:
        pages_str: String representation of page ranges
        
    Returns:
        Set of page numbers
        
    Example:
        "1-3,5,7-9" returns {1, 2, 3, 5, 7, 8, 9}
    """
    if not pages_str:
        return set()
        
    pages = set()
    for part in pages_str.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    return pages


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string to be used as a filename
    
    Args:
        filename: The input string to sanitize
        
    Returns:
        A sanitized filename string
    """
    # Replace any non-alphanumeric character with underscore
    sanitized = re.sub(r'[^\w\-\.]', '_', filename)
    return sanitized 