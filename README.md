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

# Choose where the PDF is written (file or existing directory)
cvforge cv.yaml -o dist/resume.pdf

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
- Quote values that must appear exactly, such as `gpa: "3.80"`. Unquoted
  numbers and dates are accepted, but YAML reads `3.80` as `3.8`.
- Unknown fields are ignored with a warning (and a suggestion for typos such as
  `experiance`).
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
| `language` | No | Section headings language: built-in `"en"` (default) or `"tr"`; other codes use English headings unless `section-titles` is set. Does not translate content. |
| `font` | No | Font family (run `cvforge fonts` to see available options). CVForge warns when the font is not installed and names the fallback it uses. |
| `paper` | No | `"a4"` (default) or `"letter"` |
| `font-size` | No | Body text size, e.g. `"10pt"` (default) or `"9.5pt"` |
| `margin` | No | Page margin in `pt`, `mm`, `cm`, or `in` (default: `"0.5in"`) |
| `section-titles` | No | Mapping that overrides section headings, e.g. `experience: "Work History"` |
| `name` | **Yes**| Your full name |
| `role` | **Yes**| Job title / professional role |
| `email` | **Yes**| Contact email |
| `phone` | No | Phone number |
| `location` | No | City, Country |
| `website` | No | Personal website URL |
| `website-text` | No | Custom display text for the website link (default: the URL) |
| `linkedin` | No | LinkedIn profile URL |
| `linkedin-text`| No | Custom display text for the LinkedIn link (default: the URL) |
| `github` | No | GitHub profile URL |
| `github-text` | No | Custom display text for the GitHub link (default: the URL) |
| `photo` | No | Local path to your profile photo, resolved relative to the YAML file |
| `photo-width` | No | Photo display width in `pt`, `mm`, `cm`, or `in` (default: `"2.5cm"`) |
| `summary` | No | Professional summary paragraph |
| `skills` | No | List of skill groups with `category` and `items` (`Category`/`Items` also work) |
| `experience` | No | List of work entries with optional `description` bullet lists |
| `education` | No | List of education entries with optional `description` bullet lists |
| `projects` | No | List of project entries with optional `description` bullet lists |
| `certifications`| No | List of certification entries |
| `awards` | No | List of award entries |
| `languages` | No | List of language proficiency entries |
| `interests` | No | List of interest/hobby strings |

Section entries accept these fields:

| Section | Fields |
|---------|--------|
| `experience` | `company`, `role`, `date`, `location`, `description` |
| `education` | `school`, `degree`, `date`, `location`, `gpa`, `description` |
| `projects` | `name`, `date`, `url`, `url-text`, `role`, `description` |
| `certifications` | `name`, `issuer`, `date` |
| `awards` | `name`, `issuer`, `date` |
| `languages` | `name`, `level` |

`description` is a list of bullet strings.

Contact links show the URL itself by default (for example `github.com/you`),
because ATS parsers read the visible text rather than the link target. Set
`github-text`, `linkedin-text`, or `website-text` to show a label instead.

### Inline Bold Formatting

Use double underscores to make text bold in narrative fields (summary, descriptions, skills, etc.):

```yaml
summary: "Built and scaled __high-throughput APIs__ for fintech workloads."
```

Double underscores inside a word, such as `my__var`, stay literal. To show
literal double underscores elsewhere, escape them with a backslash in single
quotes or unquoted text:

```yaml
summary: 'Implemented Python \__init\__ hooks.'
```

In double-quoted YAML strings, write `\\__` instead.

---

## Features

- **Cross-platform**: Linux, Windows, macOS
- **ATS Compatible**: Clean, parseable text + built-in checker (`cvforge ats-check`)
- **Multi-language Headers**: EN/TR out of the box, any language via `section-titles`
- **Typography Choices**: 17 available fonts (`cvforge fonts`), plus paper size, font size, and margin settings
- **Rich Formatting**: Inline bolding via `__text__`, profile photo support
- **100% Local & Private**: No cloud storage, no online rendering

---

## Agent Skill

Use the [CVForge agent skill](https://github.com/SoAp9035/cvforge-skill) to help coding agents create, edit, build, and validate CVForge resumes.

---

## Development

```bash
uv sync
uv run pytest
```

---

## Support

If you find this project useful, consider supporting its development:

<a href="https://www.buymeacoffee.com/soap9035" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="40"></a>

---

## License

This project is licensed under the [MIT License](LICENSE).
