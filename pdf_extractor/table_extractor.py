"""
Module for extracting tables from PDF files using pdfplumber
"""
import os
import json
import logging
import pdfplumber
import pandas as pd
from typing import List, Set, Dict, Any, Optional
from pathlib import Path

from .utils import ensure_output_dir, sanitize_filename


class TableExtractor:
    """
    Extract tables from PDF files using pdfplumber
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the table extractor
        
        Args:
            logger: Logger object for logging messages
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def extract_tables(self, pdf_path: str, pages: Optional[Set[int]] = None,
                      output_dir: str = "output", 
                      output_format: str = "csv") -> List[str]:
        """
        Extract tables from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            pages: Set of page numbers to extract tables from (1-indexed).
                  If None, extract from all pages.
            output_dir: Directory to save output files
            output_format: Format to save tables (csv or json)
            
        Returns:
            List of paths to the output files
        """
        if output_format not in ["csv", "json"]:
            raise ValueError("Output format must be 'csv' or 'json'")
            
        output_dir = ensure_output_dir(output_dir)
        pdf_filename = Path(pdf_path).stem
        output_files = []
        
        self.logger.info(f"Extracting tables from {pdf_path}")
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Determine which pages to process
                if pages:
                    # pdfplumber is 0-indexed, but our interface is 1-indexed
                    page_indices = [p - 1 for p in pages if 0 < p <= len(pdf.pages)]
                    if len(page_indices) < len(pages):
                        self.logger.warning(f"Some requested pages are out of range. PDF has {len(pdf.pages)} pages.")
                    pdf_pages = [pdf.pages[i] for i in page_indices]
                else:
                    pdf_pages = pdf.pages

                # Process each page
                for i, page in enumerate(pdf_pages):
                    page_number = page.page_number + 1  # Convert back to 1-indexed
                    tables = page.extract_tables()
                    
                    if not tables:
                        self.logger.info(f"No tables found on page {page_number}")
                        continue
                        
                    self.logger.info(f"Found {len(tables)} tables on page {page_number}")
                    
                    # Process each table
                    for table_idx, table_data in enumerate(tables):
                        # Convert table data to DataFrame
                        # First row is header if it has different formatting
                        if not table_data:
                            continue
                            
                        df = pd.DataFrame(table_data[1:], columns=table_data[0])
                        
                        # Generate output filename
                        output_basename = f"{sanitize_filename(pdf_filename)}_page{page_number}_table{table_idx+1}"
                        
                        # Save table based on requested format
                        if output_format == "csv":
                            output_file = os.path.join(output_dir, f"{output_basename}.csv")
                            df.to_csv(output_file, index=False)
                        else:  # json
                            output_file = os.path.join(output_dir, f"{output_basename}.json")
                            df.to_json(output_file, orient="records", indent=2)
                            
                        output_files.append(output_file)
                        self.logger.info(f"Table saved to {output_file}")
                
                if not output_files:
                    self.logger.info("No tables were found in the PDF")
                    
                return output_files
                
        except Exception as e:
            self.logger.error(f"Error extracting tables: {e}")
            raise 