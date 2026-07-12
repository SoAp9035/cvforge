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
# Initialize a complete template cv.yaml
cvforge init

# Generate PDF from your YAML file
cvforge cv.yaml

# List all available fonts
cvforge fonts

# Verify ATS compatibility of generated PDF
cvforge ats-check <file.pdf>
```

---

## Configuration & YAML Structure

Run `cvforge init` to generate a complete example `cv.yaml` file with all
fields and compact comments.

### Writing `cv.yaml`

- Keep `name`, `role`, and `email` present and non-empty.
- Keep top-level sections in the order you want them rendered. CVForge renders
  resume sections in YAML order.
- Use the documented field names and list shapes. Unsupported top-level
  sections are ignored unless you also customize the Typst template.
- Use `__text__` for inline bold emphasis in summaries, bullets, skills, and
  similar narrative fields.
- Keep facts accurate. Do not add employers, dates, credentials, tools, or
  metrics unless they are real and supplied.
- Use compact, achievement-focused bullets. One or two pages is usually best
  for ATS parsing.
- For photos, set `photo` to a local path relative to the YAML file. Use simple
  `photo-width` values such as `"2.5cm"`, `"3cm"`, `"2in"`, or `"80pt"`.
- After editing, build with `cvforge cv.yaml` and check the PDF with
  `cvforge ats-check cv.pdf`.

Below is the full reference:

| Field | Required | Description |
|-------|:--------:|-------------|
| `language` | No | Section headings language: `"en"` (default) or `"tr"`. Does not translate content. |
| `font` | No | Font family (run `cvforge fonts` to see available options). |
| `name` | **Yes**| Your full name |
| `role` | **Yes**| Job title / professional role |
| `email` | **Yes**| Contact email |
| `phone` | No | Phone number |
| `location` | No | City, Country |
| `website` | No | Personal website URL |
| `website-text` | No | Custom display text for the website link |
| `linkedin` | No | LinkedIn profile URL |
| `linkedin-text`| No | Custom display text for the LinkedIn link |
| `github` | No | GitHub profile URL |
| `github-text` | No | Custom display text for the GitHub link |
| `photo` | No | Local path to your profile photo, resolved relative to the YAML file |
| `photo-width` | No | Photo display width (default: `"2.5cm"`; examples: `"3cm"`, `"2in"`, `"80pt"`) |
| `summary` | No | Professional summary paragraph |
| `skills` | No | List of skill categories with `Category` and `Items` |
| `experience` | No | List of work entries with optional `description` bullet lists |
| `education` | No | List of education entries with optional `description` bullet lists |
| `projects` | No | List of project entries with optional `description` bullet lists |
| `certifications`| No | List of certification entries |
| `awards` | No | List of award entries |
| `languages` | No | List of language proficiency entries |
| `interests` | No | List of interest/hobby strings |

### Inline Bold Formatting

Use double underscores to make text bold in narrative fields (summary, descriptions, skills, etc.):

```yaml
summary: "Built and scaled __high-throughput APIs__ for fintech workloads."
```

---

## Features

- **Cross-platform**: Linux, Windows, macOS
- **ATS Compatible**: Clean, parseable text + built-in checker (`cvforge ats-check`)
- **Multi-language Headers**: Support for EN/TR out of the box
- **Typography Choices**: 17 available fonts (`cvforge fonts`)
- **Rich Formatting**: Inline bolding via `__text__`, profile photo support
- **100% Local & Private**: No cloud storage, no online rendering

---

## Agent Skill

Use the [CVForge agent skill](https://github.com/SoAp9035/cvforge-skill) to help coding agents create, edit, build, and validate CVForge resumes.

---

## Support

If you find this project useful, consider supporting its development:

<a href="https://www.buymeacoffee.com/soap9035" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="40"></a>

---

## License

This project is licensed under the [MIT License](LICENSE).
