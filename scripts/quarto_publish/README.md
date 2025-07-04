# Quarto Publishing Scripts

This directory contains scripts for building, compressing, and publishing Quarto books to GitHub Pages.

## Scripts

### publish.sh

A comprehensive bash script for the complete publishing workflow with virtual environment support.

**Features:**
- Virtual environment management
- Git operations (commit, push)
- Quarto rendering
- PDF compression using Ghostscript
- GitHub Pages publishing
- Colored output and logging
- Error handling and retry logic

**Usage:**
```bash
./publish.sh [OPTIONS]

Options:
    -h, --help              Show help message
    -b, --branch BRANCH     Branch to publish from (default: dev)
    -m, --message MSG       Custom commit message
    --skip-git              Skip git operations
    --skip-compress         Skip PDF compression
    --skip-render           Skip Quarto rendering
    --debug                 Enable debug output
    --clean                 Clean build directories before starting

Examples:
    ./publish.sh                                  # Normal publish workflow
    ./publish.sh --skip-git                       # Skip git operations
    ./publish.sh -m "Custom commit message"       # Use custom commit message
    ./publish.sh --skip-compress --skip-render    # Only publish pre-built files
```

### render_compress_publish.py

A Python script with similar functionality plus ePub support and more advanced features.

**Features:**
- All features from publish.sh
- ePub rendering and image compression
- Multiple output format support
- Advanced logging with colors
- Automatic virtual environment setup

**Usage:**
```bash
./render_compress_publish.py [OPTIONS]

Options:
    --pdf/--no-pdf          Render to PDF (default: True)
    --epub/--no-epub        Render to ePub (default: True)
    --html/--no-html        Render to HTML (default: True)
    --compress/--no-compress Compress output files (default: True)
    --quality N             Compression quality (default: 60)
    --publish/--no-publish  Publish to GitHub Pages (default: True)
    --clean                 Clean build directories first
    --debug                 Enable debug output

Examples:
    ./render_compress_publish.py                    # Build all formats and publish
    ./render_compress_publish.py --no-publish       # Build only, don't publish
    ./render_compress_publish.py --pdf --no-epub --no-html  # Build PDF only
    ./render_compress_publish.py --quality 40       # Use lower quality for smaller files
```

### gs_compress_pdf.py

A standalone PDF compression utility using Ghostscript.

**Usage:**
```bash
python gs_compress_pdf.py -i input.pdf -o output.pdf [OPTIONS]

Options:
    -i, --input FILE        Input PDF file
    -o, --output FILE       Output PDF file
    -s, --settings PRESET   PDF settings (default: /printer)
                           Options: /screen, /ebook, /printer, /prepress
    -c, --compatibility VER PDF compatibility (default: 1.4)
    -d, --debug            Enable debug mode
```

## Requirements

### System Requirements

- **Git**: Version control
- **Quarto**: v1.3 or later
- **Python**: 3.7 or later
- **Ghostscript**: For PDF compression

### Python Dependencies

Install Python dependencies using:
```bash
pip install -r requirements.txt
```

Or let the scripts automatically set up a virtual environment.

## Virtual Environment

Both `publish.sh` and `render_compress_publish.py` automatically create and manage a Python virtual environment in `./venv/`. This ensures consistent dependencies without affecting your system Python installation.

## Logging

All scripts create logs in `publish_log.txt` in the project root directory. Logs include timestamps and are appended to preserve history.

## Troubleshooting

### Common Issues

1. **"Command not found" errors**
   - Ensure all system requirements are installed
   - Check that scripts are executable: `chmod +x *.sh *.py`

2. **Git errors**
   - Ensure you're on the correct branch (default: dev)
   - Use `--skip-git` to bypass git operations

3. **Quarto errors**
   - Check that Quarto is installed: `quarto --version`
   - Ensure all book files are valid

4. **Compression errors**
   - Install Ghostscript: `apt-get install ghostscript` (Linux) or `brew install ghostscript` (macOS)
   - For ePub compression, Pillow will be installed automatically

## Contributing

When modifying these scripts:
1. Test all changes thoroughly
2. Update this README if adding new features
3. Maintain backward compatibility
4. Follow existing code style and conventions