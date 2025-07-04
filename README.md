# EE513: Embedded Systems Design with Silicon Labs EFR32xG24

Course material and lab book for EE513 at Clarkson University focusing on embedded systems design using the Silicon Labs EFR32xG24 BLE microcontroller.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Publishing](#publishing)
- [Development](#development)
- [Documentation](#documentation)
- [License](#license)

## Overview

This repository contains the source materials for the EE513 Embedded Systems Design course textbook. The book covers embedded machine learning applications using the Silicon Labs EFR32xG24 BLE microcontroller, including topics such as gesture recognition, anomaly detection, and posture classification.

The book is built using [Quarto](https://quarto.org/), an open-source scientific and technical publishing system that supports dynamic content and multiple output formats.

## Quick Start

### Prerequisites

Before setting up the project, ensure you have the following installed:

1. **Quarto** (version 1.3 or later)
   - Download from: https://quarto.org/docs/get-started/
   - Installation guide: https://quarto.org/docs/download/

2. **Git** (for version control)
   - Download from: https://git-scm.com/downloads

3. **A text editor or IDE** (recommended)
   - VS Code with Quarto extension
   - RStudio
   - Any text editor of your choice

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/clarkson-edge/ee513_book.git
   cd ee513_book
   ```

2. **Verify Quarto installation**
   ```bash
   quarto --version
   ```

3. **Preview the book locally**
   ```bash
   quarto preview
   ```
   This will start a local server and open the book in your default browser. The preview will automatically reload when you make changes to the source files.

### Building the Book

To build the book for production:

```bash
quarto render
```

This will generate the book in the `_book` directory with all HTML files, assets, and search functionality.

### Building PDF Version (Optional)

To generate a PDF version of the book:

```bash
quarto render --to titlepage-pdf
```

Note: PDF generation requires a LaTeX installation (e.g., TinyTeX or MiKTeX).

## Project Structure

```
ee513_book/
├── _quarto.yml          # Main Quarto configuration
├── index.qmd            # Book homepage
├── contents/            # Chapter content
│   └── core/           # Core chapters
│       ├── *.qmd       # Chapter files
│       └── img/        # Chapter images
├── _book/              # Generated output (git-ignored)
├── styles/             # Custom CSS styles
├── _extensions/        # Quarto extensions
└── scripts/            # Utility scripts
```

## Publishing

### GitHub Pages Setup

This book is configured to publish to GitHub Pages. To set up automatic publishing:

1. **Enable GitHub Pages** in your repository:
   - Go to Settings → Pages
   - Source: Deploy from a branch
   - Branch: `gh-pages` (or `main` if using docs folder)
   - Folder: `/ (root)`

2. **Manual Publishing**
   ```bash
   # Build the book
   quarto render
   
   # Publish to GitHub Pages
   quarto publish gh-pages
   ```

3. **Automatic Publishing with GitHub Actions**
   
   Create `.github/workflows/publish.yml`:
   ```yaml
   name: Publish to GitHub Pages
   
   on:
     push:
       branches: [main]
   
   jobs:
     build-deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         
         - name: Set up Quarto
           uses: quarto-dev/quarto-actions/setup@v2
           
         - name: Render and Publish
           uses: quarto-dev/quarto-actions/publish@v2
           with:
             target: gh-pages
           env:
             GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
   ```

### Custom Domain (Optional)

To use a custom domain:

1. Add a `CNAME` file in the root directory with your domain
2. Configure DNS settings with your domain provider
3. Update `_quarto.yml` if needed

## Development

### Adding New Chapters

1. Create a new `.qmd` file in `contents/core/`
2. Add the chapter to `_quarto.yml` under the `chapters` section:
   ```yaml
   chapters:
     - contents/core/your_new_chapter.qmd
   ```

### Working with Images

- Place images in `contents/core/img/`
- Reference in Quarto: `![Caption](img/image.png)`
- Use descriptive filenames and alt text

### Customizing Appearance

- Modify `style.scss` for general styling
- Use `style-light.scss` and `style-dark.scss` for theme-specific styles
- Update `_quarto.yml` for layout and functionality options

### Best Practices

1. **Version Control**
   - Commit source files (`.qmd`, images, configs)
   - Do not commit `_book/` directory
   - Use meaningful commit messages

2. **Content Guidelines**
   - Use consistent formatting
   - Include code examples with proper syntax highlighting
   - Add cross-references for easy navigation
   - Test all code examples before publishing

3. **Collaboration**
   - Create feature branches for major changes
   - Submit pull requests for review
   - Follow the contribution guidelines

## Documentation

- [Contributing Guide](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)
- [Quarto Documentation](https://quarto.org/docs/books/)
- [Published Book](https://clarkson-edge.github.io/ee513_book)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

## Contact

For questions or issues related to the book content, please open an issue in this repository or contact the course instructor at Clarkson University.
