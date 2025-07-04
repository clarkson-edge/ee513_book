#!/usr/bin/env python3
"""
Quarto Book Publishing Script

A comprehensive script to build, compress, and publish Quarto books to GitHub Pages.
Includes virtual environment management, error handling, and various publishing options.
"""

import os
import sys
import re
import subprocess
import argparse
import logging
import json
import tempfile
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Try to import optional dependencies
try:
    from zipfile import ZipFile
    HAS_ZIPFILE = True
except ImportError:
    HAS_ZIPFILE = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

DEFAULT_COMPRESSION_QUALITY = 60

# ANSI color codes for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[0;37m'
    NC = '\033[0m'  # No Color

class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds color to log messages."""
    
    COLORS = {
        'DEBUG': Colors.CYAN,
        'INFO': Colors.GREEN,
        'WARNING': Colors.YELLOW,
        'ERROR': Colors.RED,
        'CRITICAL': Colors.MAGENTA,
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, Colors.WHITE)
        record.levelname = f"{log_color}[{record.levelname}]{Colors.NC}"
        return super().format(record)

class QuartoPublisher:
    """Main class for handling Quarto book publishing workflow."""
    
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.script_dir = Path(__file__).parent.absolute()
        self.project_root = self.script_dir.parent.parent
        self.venv_dir = self.script_dir / "venv"
        self.log_file = self.project_root / "publish_log.txt"
        
        # Setup logging
        self._setup_logging()
        
        # Log initial info
        self.logger.info(f"Starting publish workflow at {datetime.now()}")
        self.logger.info(f"Working directory: {self.project_root}")
        
    def _setup_logging(self):
        """Setup logging configuration."""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        # Console handler with color
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ColoredFormatter(log_format))
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, mode='a')
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # Setup logger
        self.logger = logging.getLogger('QuartoPublisher')
        self.logger.setLevel(logging.DEBUG if self.args.debug else logging.INFO)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        
    def run(self) -> int:
        """Run the complete publishing workflow."""
        try:
            # Change to project root
            os.chdir(self.project_root)
            
            # Check requirements
            self._check_requirements()
            
            # Setup virtual environment if needed
            if self.args.epub and not self.args.no_compress:
                self._setup_venv()
            
            # Clean if requested
            if self.args.clean:
                self._clean_build_directories()
            
            # Render HTML
            if self.args.html:
                self._render_html()
            
            # Render PDF
            if self.args.pdf:
                pdf_path = self._render_pdf()
                if self.args.compress and pdf_path:
                    self._compress_pdf(pdf_path)
            
            # Render ePub
            if self.args.epub:
                epub_path = self._render_epub()
                if self.args.compress and epub_path and HAS_ZIPFILE and HAS_PIL:
                    self._compress_epub(epub_path)
            
            # Publish to GitHub Pages
            if self.args.publish:
                self._publish_to_github_pages()
            
            # Success message
            self.logger.info("Publish workflow completed successfully!")
            if self.args.publish:
                self.logger.info(f"Published site: https://clarkson-edge.github.io/ee513_book")
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Publishing failed: {str(e)}")
            if self.args.debug:
                import traceback
                self.logger.error(traceback.format_exc())
            return 1
    
    def _check_requirements(self):
        """Check that all required commands are available."""
        self.logger.info("Checking required commands...")
        
        required_commands = {
            'quarto': 'Quarto publishing system',
            'python3': 'Python 3 interpreter',
        }
        
        if self.args.pdf and self.args.compress:
            required_commands['gs'] = 'Ghostscript for PDF compression'
        
        missing = []
        for cmd, description in required_commands.items():
            if not self._command_exists(cmd):
                missing.append(f"{cmd} ({description})")
        
        if missing:
            self.logger.error("Missing required commands:")
            for cmd in missing:
                self.logger.error(f"  - {cmd}")
            raise RuntimeError("Please install missing commands and try again")
            
    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH."""
        return shutil.which(command) is not None
    
    def _run_command(self, cmd: List[str], check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
        """Run a command with proper error handling."""
        self.logger.debug(f"Running command: {' '.join(cmd)}")
        
        kwargs = {
            'check': check,
            'text': True
        }
        
        if capture_output:
            kwargs['capture_output'] = True
        
        try:
            result = subprocess.run(cmd, **kwargs)
            return result
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {' '.join(cmd)}")
            if hasattr(e, 'stderr') and e.stderr:
                self.logger.error(f"Error output: {e.stderr}")
            raise
    
    def _setup_venv(self):
        """Setup and activate Python virtual environment."""
        self.logger.info("Setting up Python virtual environment...")
        
        # Create venv if it doesn't exist
        if not self.venv_dir.exists():
            self.logger.info("Creating virtual environment...")
            self._run_command([sys.executable, '-m', 'venv', str(self.venv_dir)])
        
        # Get pip path in venv
        pip_path = self.venv_dir / 'bin' / 'pip'
        
        # Upgrade pip
        self._run_command([str(pip_path), 'install', '--quiet', '--upgrade', 'pip'])
        
        # Install requirements
        requirements_file = self.script_dir / 'requirements.txt'
        if requirements_file.exists():
            self.logger.info("Installing Python dependencies...")
            self._run_command([str(pip_path), 'install', '--quiet', '-r', str(requirements_file)])
        
        # Install PIL if needed for ePub compression
        if self.args.epub and self.args.compress and not HAS_PIL:
            self.logger.info("Installing Pillow for ePub image compression...")
            self._run_command([str(pip_path), 'install', '--quiet', 'Pillow'])
    
    def _clean_build_directories(self):
        """Clean build directories."""
        self.logger.info("Cleaning build directories...")
        
        for dir_name in ['_site', '_book']:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                self.logger.debug(f"Removed {dir_path}")
        
        self._run_command(['git', 'worktree', 'prune'], check=False)
    
    def _render_html(self):
        """Render the Quarto book to HTML."""
        self.logger.info("Rendering book to HTML...")
        
        cmd = ['quarto', 'render', '--no-clean', '--to', 'html']
        if not self.args.debug:
            cmd.append('--quiet')
        
        self._run_command(cmd)
        self.logger.info("HTML render completed successfully")
    
    def _render_pdf(self) -> Optional[Path]:
        """Render the Quarto book to PDF."""
        self.logger.info("Rendering book to PDF...")
        
        cmd = ['quarto', 'render', '--no-clean', '--to', 'titlepage-pdf']
        
        result = self._run_command(cmd, capture_output=True)
        
        # Extract PDF path from output
        pdf_path = None
        for line in result.stdout.splitlines() + result.stderr.splitlines():
            match = re.search(r'Output created: (.+\.pdf)', line)
            if match:
                pdf_path = Path(match.group(1))
                break
        
        if pdf_path and pdf_path.exists():
            self.logger.info(f"PDF created: {pdf_path}")
            return pdf_path
        else:
            self.logger.error("PDF file not found in output")
            return None
    
    def _render_epub(self) -> Optional[Path]:
        """Render the Quarto book to ePub."""
        self.logger.info("Rendering book to ePub...")
        
        cmd = ['quarto', 'render', '--no-clean', '--to', 'epub']
        
        result = self._run_command(cmd, capture_output=True)
        
        # Extract ePub path from output
        epub_path = None
        for line in result.stdout.splitlines() + result.stderr.splitlines():
            match = re.search(r'Output created: (.+\.epub)', line)
            if match:
                epub_path = Path(match.group(1))
                break
        
        if epub_path and epub_path.exists():
            self.logger.info(f"ePub created: {epub_path}")
            return epub_path
        else:
            self.logger.error("ePub file not found in output")
            return None
    
    def _compress_pdf(self, pdf_path: Path):
        """Compress the PDF using ghostscript."""
        self.logger.info("Compressing PDF...")
        
        # Measure original size
        original_size = pdf_path.stat().st_size
        self.logger.info(f"Original PDF size: {self._format_size(original_size)}")
        
        # Create temporary file
        temp_pdf = pdf_path.parent / f"{pdf_path.stem}_compressed.pdf"
        
        # Run ghostscript compression
        cmd = [
            'gs',
            '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.4',
            f'-dPDFSETTINGS=/ebook',
            '-dNOPAUSE',
            '-dQUIET',
            '-dBATCH',
            f'-sOutputFile={temp_pdf}',
            str(pdf_path)
        ]
        
        self._run_command(cmd)
        
        # Check compressed size
        compressed_size = temp_pdf.stat().st_size
        compression_ratio = (1.0 - (compressed_size / original_size)) * 100
        
        self.logger.info(f"Compressed PDF size: {self._format_size(compressed_size)}")
        self.logger.info(f"Compression ratio: {compression_ratio:.2f}%")
        
        # Replace original with compressed
        temp_pdf.replace(pdf_path)
        self.logger.info("PDF compression completed")
    
    def _compress_epub(self, epub_path: Path):
        """Compress images in the ePub file."""
        if not HAS_ZIPFILE or not HAS_PIL:
            self.logger.warning("Skipping ePub compression (missing dependencies)")
            return
        
        self.logger.info("Compressing ePub images...")
        
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Extract ePub
            with ZipFile(epub_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find and compress images
            image_files = []
            for pattern in ['*.png', '*.jpg', '*.jpeg', '*.gif']:
                image_files.extend(temp_dir.rglob(pattern))
            
            total_original = 0
            total_compressed = 0
            
            for img_path in image_files:
                original_size = img_path.stat().st_size
                total_original += original_size
                
                try:
                    img = Image.open(img_path)
                    img.save(img_path, optimize=True, quality=self.args.quality)
                    
                    compressed_size = img_path.stat().st_size
                    total_compressed += compressed_size
                    
                    self.logger.debug(f"Compressed {img_path.name}: {self._format_size(original_size)} -> {self._format_size(compressed_size)}")
                except Exception as e:
                    self.logger.warning(f"Failed to compress {img_path.name}: {e}")
                    total_compressed += original_size
            
            # Repackage ePub
            temp_epub = epub_path.parent / f"{epub_path.stem}_compressed.epub"
            with ZipFile(temp_epub, 'w') as zip_ref:
                for file_path in temp_dir.rglob('*'):
                    if file_path.is_file():
                        zip_ref.write(file_path, file_path.relative_to(temp_dir))
            
            # Replace original
            temp_epub.replace(epub_path)
            
            if total_original > 0:
                compression_ratio = (1.0 - (total_compressed / total_original)) * 100
                self.logger.info(f"ePub image compression ratio: {compression_ratio:.2f}%")
            
        finally:
            shutil.rmtree(temp_dir)
    
    def _publish_to_github_pages(self):
        """Publish to GitHub Pages."""
        self.logger.info("Publishing to GitHub Pages...")
        
        cmd = ['quarto', 'publish', 'gh-pages', '--no-render', '--no-prompt']
        
        try:
            self._run_command(cmd)
            self.logger.info("Successfully published to GitHub Pages")
        except subprocess.CalledProcessError:
            self.logger.warning("First publish attempt failed, retrying...")
            
            # Clean and retry
            self._run_command(['rm', '-rf', '_site'], check=False)
            self._run_command(['git', 'worktree', 'prune'], check=False)
            
            self._run_command(cmd)
            self.logger.info("Successfully published to GitHub Pages (on retry)")
    
    def _format_size(self, size_bytes: int) -> str:
        """Format bytes to human readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build and publish Quarto book with compression support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s                                    # Build all formats and publish
    %(prog)s --no-publish                       # Build only, don't publish
    %(prog)s --pdf --no-epub --no-html         # Build PDF only
    %(prog)s --quality 40                       # Use lower quality for smaller files
    %(prog)s --clean                            # Clean build directories first
        """
    )
    
    # Output format options
    parser.add_argument('--pdf', action='store_true', default=True,
                        help='Render to PDF (default: True)')
    parser.add_argument('--epub', action='store_true', default=True,
                        help='Render to ePub (default: True)')
    parser.add_argument('--html', action='store_true', default=True,
                        help='Render to HTML (default: True)')
    
    # Negative options
    parser.add_argument('--no-pdf', dest='pdf', action='store_false',
                        help="Don't render to PDF")
    parser.add_argument('--no-epub', dest='epub', action='store_false',
                        help="Don't render to ePub")
    parser.add_argument('--no-html', dest='html', action='store_false',
                        help="Don't render to HTML")
    
    # Compression options
    parser.add_argument('--compress', action='store_true', default=True,
                        help='Compress output files (default: True)')
    parser.add_argument('--no-compress', dest='compress', action='store_false',
                        help="Don't compress output files")
    parser.add_argument('--quality', type=int, default=DEFAULT_COMPRESSION_QUALITY,
                        help='Compression quality for images (default: %(default)s)')
    
    # Publishing options
    parser.add_argument('--publish', action='store_true', default=True,
                        help='Publish to GitHub Pages (default: True)')
    parser.add_argument('--no-publish', dest='publish', action='store_false',
                        help="Don't publish to GitHub Pages")
    
    # Other options
    parser.add_argument('--clean', action='store_true',
                        help='Clean build directories before starting')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug output')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.pdf, args.epub, args.html]):
        parser.error("At least one output format must be enabled")
    
    # Create publisher instance and run
    publisher = QuartoPublisher(args)
    sys.exit(publisher.run())

if __name__ == '__main__':
    main()