#!/usr/bin/env python3
"""
Main CLI module for PDF Extractor
"""
import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional, Set
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich import print as rprint

from pdf_extractor.utils import setup_logging, parse_page_ranges
from pdf_extractor.text_extractor import TextExtractor
from pdf_extractor.table_extractor import TableExtractor
from pdf_extractor.image_extractor import ImageExtractor
from pdf_extractor.ocr_extractor import OCRExtractor


def create_parser() -> argparse.ArgumentParser:
    """
    Create the command line argument parser
    
    Returns:
        ArgumentParser object
    """
    parser = argparse.ArgumentParser(
        description="Extract data from PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Extract plain text from a PDF
    pdf-extractor-cli --file document.pdf --text
    
    # Extract tables as CSV from pages 1 to 3
    pdf-extractor-cli --file document.pdf --tables --pages 1-3
    
    # Extract images from a PDF
    pdf-extractor-cli --file document.pdf --images
    
    # Apply OCR to extract text from images in a PDF
    pdf-extractor-cli --file document.pdf --ocr
    
    # Extract text, tables and apply OCR to specific pages
    pdf-extractor-cli --file document.pdf --text --tables --ocr --pages 1,5-7
        """
    )
    
    parser.add_argument("--file", required=True, help="Path to the PDF file")
    parser.add_argument("--text", action="store_true", help="Extract plain text")
    parser.add_argument("--tables", action="store_true", help="Extract tables")
    parser.add_argument("--images", action="store_true", help="Extract images")
    parser.add_argument("--ocr", action="store_true", help="Apply OCR to images")
    parser.add_argument("--pages", help="Page numbers or ranges to process (e.g. 1-3,5,7)")
    parser.add_argument("--output", default="output", help="Output directory")
    parser.add_argument("--table-format", choices=["csv", "json"], default="csv",
                       help="Output format for tables (csv or json)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    return parser


def main() -> int:
    """
    Main entry point for the application
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Configure console for rich output
    console = Console()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level)
    
    # Parse pages if specified
    pages = parse_page_ranges(args.pages) if args.pages else None
    
    # Validate input file
    if not os.path.isfile(args.file):
        console.print(f"[bold red]Error:[/] PDF file not found: {args.file}")
        return 1
        
    # Display header
    console.print(Panel.fit(
        "[bold blue]PDF Extractor CLI[/]",
        subtitle=f"Processing: [green]{os.path.basename(args.file)}[/green]"
    ))
    
    # Check if at least one extraction option was selected
    if not any([args.text, args.tables, args.images, args.ocr]):
        console.print("[bold yellow]Warning:[/] No extraction options selected. "
                     "Use --text, --tables, --images, or --ocr.")
        parser.print_help()
        return 1
    
    # Process the PDF file with the selected options
    try:
        if args.text:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]Extracting text..."),
                BarColumn(),
                TimeElapsedColumn()
            ) as progress:
                task = progress.add_task("Extracting...", total=1)
                extractor = TextExtractor(logger)
                output_file = extractor.extract_text(args.file, pages, args.output)
                progress.update(task, advance=1)
            console.print(f"[green]✓[/] Text extracted to: [bold]{output_file}[/]")
        
        if args.tables:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]Extracting tables..."),
                BarColumn(),
                TimeElapsedColumn()
            ) as progress:
                task = progress.add_task("Extracting...", total=1)
                extractor = TableExtractor(logger)
                output_files = extractor.extract_tables(
                    args.file, pages, args.output, args.table_format
                )
                progress.update(task, advance=1)
            
            if output_files:
                console.print(f"[green]✓[/] {len(output_files)} tables extracted to: [bold]{args.output}[/]")
            else:
                console.print("[yellow]![/] No tables found in the document")
        
        if args.images:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]Extracting images..."),
                BarColumn(),
                TimeElapsedColumn()
            ) as progress:
                task = progress.add_task("Extracting...", total=1)
                extractor = ImageExtractor(logger)
                output_files = extractor.extract_images(args.file, pages, args.output)
                progress.update(task, advance=1)
                
            if output_files:
                console.print(f"[green]✓[/] {len(output_files)} images extracted to: [bold]{args.output}[/]")
            else:
                console.print("[yellow]![/] No images found in the document")
        
        if args.ocr:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]Applying OCR..."),
                BarColumn(),
                TimeElapsedColumn()
            ) as progress:
                task = progress.add_task("Processing...", total=1)
                extractor = OCRExtractor(logger)
                output_file = extractor.extract_text_with_ocr(args.file, pages, args.output)
                progress.update(task, advance=1)
            console.print(f"[green]✓[/] OCR text extracted to: [bold]{output_file}[/]")
        
        console.print("\n[bold green]✓ All tasks completed successfully![/]")
        return 0
        
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        if args.verbose:
            console.print_exception()
        return 1


if __name__ == "__main__":
    sys.exit(main())
 