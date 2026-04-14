# CVForge

[![PyPI version](https://badge.fury.io/py/cvforge.svg)](https://badge.fury.io/py/cvforge) [![Downloads](https://pepy.tech/badge/cvforge)](https://pepy.tech/project/cvforge) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

CVForge is a CLI that turns a YAML file into a clean, ATS-friendly PDF resume using Typst. Edit your content, rerun the command, and regenerate the same layout locally. Ideal for fast iteration and version control.

---

## Why This Tool?

I created CVForge because I needed a fast, reliable way to build and rebuild my resume without:

- Using Word or clunky desktop apps
- Trusting random online resume builders with my personal data
- Spending time on formatting instead of content

CVForge lets you define your CV once in YAML and regenerate it instantly. Change a job title, add a skill, rebuild — done. **100% local, 100% private.**

---

## Installation

### Using [UV](https://docs.astral.sh/uv/) (Recommended)

```bash
# Install as a tool
uv tool install cvforge

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

# Uninstall
pip uninstall cvforge
```

---

## Usage

```bash
# Initialize a new CV
cvforge init

# Generate PDF from YAML
cvforge cv.yaml
```

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

### Inline Bold Formatting

Use double underscores to make text bold in narrative fields:

```yaml
summary: "Built and scaled __high-throughput APIs__ for fintech workloads."
```

`__text__` renders as bold in fields like summary, skills, descriptions, languages, certifications, awards, and interests. Unmatched double underscores stay literal.

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
