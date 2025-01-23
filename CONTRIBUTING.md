```markdown
# Contributing to EE513 Book

## Development Workflow

1. **Fork and Setup**
```bash
git clone https://github.com/YOUR_USERNAME/ee513_book.git
cd ee513_book
git remote add upstream https://github.com/clarkson-edge/ee513_book.git
```

2. **Branch Guidelines**
- Branch from `dev`
- Name format: `issue<number>-description`
- Keep changes focused
- Rebase before PR

3. **Content Structure**
```
ee513_book/
├── _quarto.yml      # Configuration
├── contents/
│   └── core/        # Chapters
│       ├── *.qmd    # Content files
│       └── img/     # Images
└── references.bib   # Bibliography
```

4. **Images**
- Save to `contents/core/img/`
- Format: `chapter-name_description.{png|jpg|svg}`
- Usage: `![Caption](img/chapter-name_description.png)`

5. **Build and Test**
```bash
quarto preview  # Live preview
quarto render   # Full build
```

6. **Publishing**
```bash
chmod +x scripts/quarto_publish/publish.sh
./scripts/quarto_publish/publish.sh
```

7. **Pull Requests**
- Submit to `dev` branch
- Reference issue number
- Add [WIP] if incomplete
- Fill template completely

## Style Guide

- Use American English
- Write in active voice
- Keep paragraphs short
- Include code examples
- Add comments for clarity
- Follow Quarto markdown specs

## Questions
Open an issue labeled 'question'
```