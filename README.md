# CVForge

A YAML-based, ATS-compatible CV/Resume generator powered by [Typst](https://github.com/typst/typst).

---

## Why This Tool?

I created CVForge because I needed a fast, reliable way to build and rebuild my resume without:

- Using Word or clunky desktop apps
- Trusting random online resume builders with my personal data
- Spending time on formatting instead of content

CVForge lets you define your CV once in YAML and regenerate it instantly. Change a job title, add a skill, rebuild — done. **100% local, 100% private.**

---

## Requirements

- **[Typst](https://github.com/typst/typst)**: Must be installed and available in your `PATH`
- **Python 3.10+**

---

## Installation

### Using UV (Recommended)

```bash
# Run without installing
uvx cvforge init
uvx cvforge cv.yaml

# Or install as a tool
uv tool install cvforge
cvforge cv.yaml

# Update
uv tool upgrade cvforge

# Uninstall
uv tool uninstall cvforge
```

### Using Pip

```bash
# Install
pip install cvforge

# Update
pip install --upgrade cvforge

# Use
cvforge cv.yaml
```

---

## Usage

| Command | Description |
|---------|-------------|
| `cvforge init` | Creates a template `cv.yaml` |
| `cvforge <file.yaml>` | Generates PDF from YAML |
| `cvforge fonts` | Lists available fonts |
| `cvforge ats-check <file.pdf>` | Checks PDF for ATS compatibility |

---

## Configuration

### Language

The `language` parameter controls the **section headings** in your CV (e.g., "Experience" vs "Deneyim"). It does not translate your content.

```yaml
language: "en"  # English headings (default)
language: "tr"  # Turkish headings
```

### Fonts

Run `cvforge fonts` to see available options. The font must be installed on your system.

```yaml
font: "roboto"  # Options: noto, roboto, inter, lato, arial, times, calibri, etc.
```

---

## YAML Structure

| Field | Required | Description |
|-------|----------|-------------|
| `language` | No | Section heading language: `"en"` (default) or `"tr"` |
| `font` | No | Font family (run `cvforge fonts` to list options) |
| `name` | Yes | Your full name |
| `role` | Yes | Job title / professional role |
| `email` | Yes | Contact email |
| `phone` | No | Phone number |
| `location` | No | City, Country |
| `website` | No | Personal website URL |
| `website-text` | No | Custom display text for website link |
| `linkedin` | No | LinkedIn profile URL |
| `linkedin-text` | No | Custom display text for LinkedIn link |
| `github` | No | GitHub profile URL |
| `github-text` | No | Custom display text for GitHub link |
| `photo` | No | Path to profile photo |
| `photo-width` | No | Photo width (default: `"2.5cm"`) |
| `summary` | No | Professional summary paragraph |
| `skills` | No | List of skill categories with items |
| `experience` | No | Work experience entries |
| `education` | No | Education entries |
| `projects` | No | Project entries |
| `certifications` | No | Certification entries |
| `awards` | No | Award entries |
| `languages` | No | Language proficiencies |
| `interests` | No | List of interests/hobbies |

> Run `cvforge init` to generate a complete example YAML file with all fields.

---

## Features

- **Cross-platform**: Linux, Windows, macOS
- **ATS Compatible**: Clean, parseable text
- **Multi-language**: EN/TR section headings
- **17 fonts** available
- **Built-in ATS checker**
- **Photo support**
- **100% Local & Private**

---

## Support

If you find this project useful, consider supporting its development:

<a href="https://www.buymeacoffee.com/soap9035" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="40"></a>

---

## License

This project is licensed under the [MIT License](LICENSE).

© 2025 Ahmet Burhan Kayalı
