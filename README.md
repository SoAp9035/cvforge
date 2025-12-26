# CVForge

**CVForge** is a straightforward, YAML-based, ATS-compatible CV/Resume generator powered by [Typst](https://typst.app/). Create professional, machine-readable resumes in seconds.

---

## 🚀 Quick Start

### Using UV (Recommended)

The fastest way to use CVForge is with [uv](https://docs.astral.sh/uv/), which is significantly faster and keeps tools isolated.

```bash
# Run instantly without installing (creates a temp environment)
uvx cvforge init        # Create a template cv.yaml
uvx cvforge cv.yaml     # Build your CV

# Or install globally as a tool
uv tool install cvforge
cvforge cv.yaml
```

### Using Pip

CVForge is available on PyPI and can be installed with standard `pip`:

```bash
pip install cvforge
cvforge cv.yaml
```

---

## 📋 Requirements

- **[Typst](https://github.com/typst/typst)**: The Typst CLI must be installed and available in your `PATH`.
- **Python 3.8+**

---

## 📖 Usage

| Command | Description |
|---------|-------------|
| `cvforge init` | Creates a template `cv.yaml` in the current directory. |
| `cvforge <file.yaml>` | Generates a PDF from the specified YAML file. |
| `cvforge fonts` | Lists all available ATS-friendly fonts. |
| `cvforge ats-check <file.pdf>` | Analyzes a PDF for ATS compatibility. |
| `cvforge --help` | Shows help information. |

### Examples

```bash
# Initialize a new CV project
cvforge init

# Build CV from default cv.yaml
cvforge cv.yaml

# Build from any YAML file
cvforge resume.yaml

# Check if your PDF is ATS-friendly
cvforge ats-check cv.pdf
```

---

## ⚙️ Configuration

### Language
```yaml
language: "en"  # English (default)
language: "tr"  # Turkish
```

### Fonts

All fonts are ATS-friendly. Use `cvforge fonts` to see the full list.

```yaml
font: "roboto"  # Options: noto, roboto, inter, lato, montserrat, opensans, etc.
```

---

## 📝 YAML Structure

```yaml
# Configuration
language: "en"
font: "noto"

# Required
name: "Your Name"

# Optional
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

# Additional sections: projects, languages, certifications, awards, interests
```

---

## ✨ Features

- ✅ **Cross-platform**: Linux, Windows, macOS
- ✅ **ATS Compatible**: Clean, selectable text
- ✅ **Multi-language**: English and Turkish section headings
- ✅ **11 ATS-friendly fonts**
- ✅ **Built-in ATS checker**
- ✅ **Optional photo support**

---

## 📦 Tool Management with UV

If you installed CVForge with `uv tool install`:

```bash
# Upgrade to latest version
uv tool upgrade cvforge

# Run a specific version
uvx cvforge@1.0.0

# Uninstall
uv tool uninstall cvforge
```

---

## 🤖 A Note

This project was fully **vibe coded** — built with AI assistance. ✨

---

## 📜 License

MIT
