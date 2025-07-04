#!/bin/bash
set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

# Default values
LOG_FILE="$PROJECT_ROOT/publish_log.txt"
BRANCH="dev"
SKIP_GIT=false
SKIP_COMPRESS=false
SKIP_RENDER=false
DEBUG=false
COMMIT_MSG=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Usage function
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    -h, --help              Show this help message
    -b, --branch BRANCH     Branch to publish from (default: dev)
    -m, --message MSG       Custom commit message
    --skip-git              Skip git operations (add, commit, push)
    --skip-compress         Skip PDF compression
    --skip-render           Skip Quarto rendering
    --debug                 Enable debug output
    --clean                 Clean build directories before starting

Examples:
    $0                                  # Normal publish workflow
    $0 --skip-git                       # Skip git operations
    $0 -m "Custom commit message"       # Use custom commit message
    $0 --skip-compress --skip-render    # Only publish pre-built files

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -b|--branch)
            BRANCH="$2"
            shift 2
            ;;
        -m|--message)
            COMMIT_MSG="$2"
            shift 2
            ;;
        --skip-git)
            SKIP_GIT=true
            shift
            ;;
        --skip-compress)
            SKIP_COMPRESS=true
            shift
            ;;
        --skip-render)
            SKIP_RENDER=true
            shift
            ;;
        --debug)
            DEBUG=true
            shift
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            exit 1
            ;;
    esac
done

# Logging setup
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')
exec 1> >(tee -a "$LOG_FILE") 2>&1
echo "Starting publish workflow at $TIMESTAMP"
echo "Working directory: $PROJECT_ROOT"

# Function to print colored messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check command existence
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed. Please install $1 and try again."
        exit 1
    fi
}

# Function to setup Python virtual environment
setup_venv() {
    log_info "Setting up Python virtual environment..."
    
    if [[ ! -d "$VENV_DIR" ]]; then
        log_info "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --quiet --upgrade pip
    
    # Install requirements
    if [[ -f "$SCRIPT_DIR/requirements.txt" ]]; then
        log_info "Installing Python dependencies..."
        pip install --quiet -r "$SCRIPT_DIR/requirements.txt"
    fi
}

# Change to project root
cd "$PROJECT_ROOT"

# Check required commands
log_info "Checking required commands..."
check_command "git"
check_command "quarto"
check_command "python3"
check_command "gs"  # Ghostscript

# Check branch if not skipping git
if [[ "$SKIP_GIT" == false ]]; then
    current_branch=$(git branch --show-current)
    if [[ "$current_branch" != "$BRANCH" ]]; then
        log_error "Not on $BRANCH branch (current: $current_branch)"
        log_info "Switch to $BRANCH branch or use --branch option"
        exit 1
    fi
    
    # Check for uncommitted changes
    if [[ -n $(git status --porcelain) ]]; then
        log_warn "Uncommitted changes detected"
    fi
fi

# Clean build directories if requested
if [[ "${CLEAN:-false}" == true ]]; then
    log_info "Cleaning build directories..."
    rm -rf _site _book
    git worktree prune
fi

# Git operations
if [[ "$SKIP_GIT" == false ]]; then
    log_info "Performing git operations..."
    
    # Add all changes
    git add .
    
    # Commit with custom or default message
    if [[ -z "$COMMIT_MSG" ]]; then
        COMMIT_MSG="Update content $(date '+%Y-%m-%d')"
    fi
    
    if git commit -m "$COMMIT_MSG"; then
        log_info "Committed changes: $COMMIT_MSG"
    else
        log_warn "No changes to commit"
    fi
    
    # Push to remote
    if git push origin "$BRANCH"; then
        log_info "Pushed to origin/$BRANCH"
    else
        log_error "Failed to push to origin/$BRANCH"
        exit 1
    fi
fi

# Render Quarto book
if [[ "$SKIP_RENDER" == false ]]; then
    log_info "Rendering Quarto book..."
    
    if [[ "$DEBUG" == true ]]; then
        quarto render
    else
        quarto render --quiet
    fi
    
    if [[ $? -ne 0 ]]; then
        log_error "Quarto render failed"
        exit 1
    fi
    log_info "Quarto render completed successfully"
fi

# Compress PDF if it exists and compression not skipped
PDF_PATH="_book/Embedded-Systems-Design.pdf"
if [[ -f "$PDF_PATH" ]] && [[ "$SKIP_COMPRESS" == false ]]; then
    log_info "Compressing PDF..."
    
    # Setup Python environment
    setup_venv
    
    # Run compression
    COMPRESS_ARGS="-i $PDF_PATH -o _book/ebook.pdf -s /ebook"
    if [[ "$DEBUG" == true ]]; then
        COMPRESS_ARGS="$COMPRESS_ARGS -d"
    fi
    
    if python "$SCRIPT_DIR/gs_compress_pdf.py" $COMPRESS_ARGS; then
        mv _book/ebook.pdf "$PDF_PATH"
        log_info "PDF compression completed"
    else
        log_error "PDF compression failed"
        exit 1
    fi
    
    # Deactivate virtual environment
    deactivate
fi

# Publish to GitHub Pages
log_info "Publishing to GitHub Pages..."

# Try publishing, with retry logic
publish_attempt=0
max_attempts=2

while [[ $publish_attempt -lt $max_attempts ]]; do
    publish_attempt=$((publish_attempt + 1))
    
    if [[ $publish_attempt -gt 1 ]]; then
        log_warn "Retrying publish (attempt $publish_attempt/$max_attempts)..."
        rm -rf _site
        git worktree prune
    fi
    
    if quarto publish gh-pages --no-render --no-prompt; then
        log_info "Successfully published to GitHub Pages"
        break
    else
        if [[ $publish_attempt -eq $max_attempts ]]; then
            log_error "Failed to publish after $max_attempts attempts"
            exit 1
        fi
    fi
done

# Summary
echo ""
log_info "Publish workflow completed successfully!"
echo "Timestamp: $(date '+%Y-%m-%d_%H-%M-%S')"
echo "Published site: https://clarkson-edge.github.io/ee513_book"
echo ""

# Cleanup on exit
trap 'deactivate 2>/dev/null || true' EXIT