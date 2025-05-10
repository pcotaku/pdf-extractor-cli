"""
Module for extracting text from PDF files using PyMuPDF (fitz)
"""
import os
import fitz
import logging
from typing import List, Set, Optional
from pathlib import Path

from .utils import ensure_output_dir, sanitize_filename


class TextExtractor:
    """
    Extract text from PDF files using PyMuPDF (fitz)
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the text extractor
        
        Args:
            logger: Logger object for logging messages
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def extract_text(self, pdf_path: str, pages: Optional[Set[int]] = None, 
                    output_dir: str = "output") -> str:
        """
        Extract text from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            pages: Set of page numbers to extract text from (1-indexed).
                  If None, extract all pages.
            output_dir: Directory to save output
            
        Returns:
            Path to the output file
        """
        output_dir = ensure_output_dir(output_dir)
        pdf_filename = Path(pdf_path).stem
        output_file = os.path.join(output_dir, f"{sanitize_filename(pdf_filename)}_text.txt")
        
        self.logger.info(f"Extracting text from {pdf_path}")
        
        try:
            with fitz.open(pdf_path) as doc:
                text_content = []
                
                # Determine which pages to process
                if pages:
                    # Convert from 1-indexed to 0-indexed
                    page_indices = [p - 1 for p in pages if 0 < p <= len(doc)]
                    if len(page_indices) < len(pages):
                        self.logger.warning(f"Some requested pages are out of range. PDF has {len(doc)} pages.")
                else:
                    page_indices = range(len(doc))
                
                # Process each page
                for i in page_indices:
                    page = doc[i]
                    text_content.append(f"--- Page {i+1} ---\n")
                    text_content.append(page.get_text())
                    text_content.append("\n\n")
                
                # Write the extracted text to a file
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write("".join(text_content))
                
                self.logger.info(f"Text extraction complete. Output saved to {output_file}")
                return output_file
                
        except Exception as e:
            self.logger.error(f"Error extracting text: {e}")
            raise 