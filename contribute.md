# Contributing to EE513 Book

## How to Contribute

1. **Fork and Setup Repository**
```bash
git clone https://github.com/YOUR_USERNAME/ee513_book.git
cd ee513_book
git remote add upstream https://github.com/clarkson-edge/ee513_book.git
```

2. **Branch and Development**
- Create branch: `issue<number>-brief-description`
- Work on your changes
- Test locally: `quarto render`

3. **Content Structure**
```
ee513_book/
├── _quarto.yml           # Book configuration
├── contents/
│   └── core/            # Chapter content
│       ├── 01-intro.qmd
│       ├── 02-setup.qmd
│       └── img/         # Image assets
└── references.bib      # Bibliography
```

4. **Update Book Structure**
- Edit `_quarto.yml` to add/modify chapters:
```yaml
project:
  type: book
book:
  chapters:
    - contents/core/01-intro.qmd
    - contents/core/02-setup.qmd
```

5. **Image Guidelines**
- Place in `contents/core/img/`
- Naming: `chapter-name_image-description.{png|jpg|svg}`
- Reference: `![Caption](img/chapter-name_image-description.png)`

6. **Submit Changes**
```bash
git add .
git commit -m "description (issue #X)"
git push origin issue-X-description
```
- Create PR to dev branch
- Add [WIP] if work in progress

## Testing
```bash
quarto preview   # Live preview
quarto render   # Build book
quarto publish  # Deploy to gh-pages
```

## Questions?
Open an issue for contribution questions.