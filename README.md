# CVForge

A YAML-based, ATS-compatible CV/Resume generator powered by [Typst](https://typst.app/).

---

## Why This Tool?

I created CVForge because I needed a fast, reliable way to build and rebuild my resume without:

- Using Word or clunky desktop apps
- Trusting random online resume builders with my personal data
- Spending time on formatting instead of content

CVForge lets you define your CV once in YAML and regenerate it instantly. Change a job title, add a skill, rebuild — done. **100% local, 100% private.**

> **Note:** I'm planning to re-build this tool from scratch with no vibe coding.

---

## Requirements

- **[Typst](https://github.com/typst/typst)**: Must be installed and available in your `PATH`
- **Python 3.8+**

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
font: "roboto"  # Options: noto, roboto, inter, lato, montserrat, opensans, etc.
```

---

## YAML Structure

```yaml
language: "en"
font: "noto"

name: "Your Name"
role: "Software Engineer"
email: "hello@example.com"
phone: "+1 555 123 4567"
location: "New York, USA"
website: "example.com"
linkedin: "linkedin.com/in/username"
github: "github.com/username"
photo: "photo.jpg"

summary: |
  A brief professional summary...

experience:
  - company: "Tech Corp"
    role: "Senior Developer"
    date: "2022 - Present"
    description:
      - "Led a team of 5 developers"
      - "Reduced latency by 40%"

education:
  - school: "University of Science"
    degree: "B.S. Computer Science"
    date: "2018 - 2022"

skills:
  - Category: "Languages"
    Items: ["Python", "Rust", "TypeScript"]

# Additional: projects, languages, certifications, awards, interests
```

---

## Features

- **Cross-platform**: Linux, Windows, macOS
- **ATS Compatible**: Clean, parseable text
- **Multi-language**: EN/TR section headings
- **11 fonts** available
- **Built-in ATS checker**
- **Photo support**
- **100% Local & Private**

---

## License

MIT
