#!/usr/bin/env python3
"""
CVForge CLI - Build ATS-friendly CVs from YAML using Typst.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from . import __version__
from .ats_checker import check_ats, PYPDF_AVAILABLE

FONT_OPTIONS = {
    "noto": ("Noto Sans", ["DejaVu Sans", "Liberation Sans", "Arial"]),
    "roboto": ("Roboto", ["Noto Sans", "DejaVu Sans", "Arial"]),
    "liberation": ("Liberation Sans", ["DejaVu Sans", "Noto Sans", "Arial"]),
    "dejavu": ("DejaVu Sans", ["Liberation Sans", "Noto Sans", "Arial"]),
    "inter": ("Inter", ["Noto Sans", "DejaVu Sans", "Arial"]),
    "lato": ("Lato", ["Noto Sans", "DejaVu Sans", "Arial"]),
    "montserrat": ("Montserrat", ["Noto Sans", "DejaVu Sans", "Arial"]),
    "raleway": ("Raleway", ["Noto Sans", "DejaVu Sans", "Arial"]),
    "ubuntu": ("Ubuntu", ["Noto Sans", "DejaVu Sans", "Arial"]),
    "opensans": ("Open Sans", ["Noto Sans", "DejaVu Sans", "Arial"]),
    "sourcesans": ("Source Sans Pro", ["Noto Sans", "DejaVu Sans", "Arial"]),
    "arial": ("Arial", ["Liberation Sans", "Noto Sans", "DejaVu Sans"]),
    "times": ("Times New Roman", ["Times", "Liberation Serif", "Noto Serif"]),
    "calibri": ("Calibri", ["Carlito", "Liberation Sans", "Arial"]),
    "georgia": ("Georgia", ["Gelasio", "Liberation Serif", "Noto Serif"]),
    "garamond": ("Garamond", ["EB Garamond", "Liberation Serif", "Noto Serif"]),
    "trebuchet": ("Trebuchet MS", ["Fira Sans", "Liberation Sans", "Arial"]),
}

DEFAULT_TEMPLATE = "ats-friendly-resume"

LANGUAGE_OPTIONS = ["en", "tr"]

SECTION_TRANSLATIONS = {
    "en": {
        "summary": "Summary",
        "skills": "Technical Skills",
        "experience": "Experience",
        "education": "Education",
        "projects": "Projects",
        "languages": "Languages",
        "certifications": "Certifications",
        "awards": "Awards",
        "interests": "Interests",
    },
    "tr": {
        "summary": "Özet",
        "skills": "Teknik Yetenekler",
        "experience": "Deneyim",
        "education": "Eğitim",
        "projects": "Projeler",
        "languages": "Diller",
        "certifications": "Sertifikalar",
        "awards": "Ödüller",
        "interests": "İlgi Alanları",
    },
}


def get_templates_dir() -> Path:
    """Get the path to the templates directory."""
    return Path(__file__).parent / "templates"


def get_template_dir(template_name: str = DEFAULT_TEMPLATE) -> Path:
    """Get the path to a specific template directory."""
    return get_templates_dir() / template_name


def check_typst_installed() -> bool:
    """Check if Typst is installed and available in PATH."""
    try:
        result = subprocess.run(
            ["typst", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def validate_yaml(yaml_path: Path) -> dict:
    """Load and validate YAML file, returning data dict."""
    if not YAML_AVAILABLE:
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if not content.strip():
                print("Error: YAML file is empty.", file=sys.stderr)
                sys.exit(1)
            return {}
        except Exception as e:
            print(f"Error reading YAML file: {e}", file=sys.stderr)
            sys.exit(1)
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            print("Error: YAML file is empty.", file=sys.stderr)
            sys.exit(1)
        
        font = data.get("font", "noto")
        if font not in FONT_OPTIONS:
            print(f"Warning: Unknown font '{font}'. Using 'noto'.", file=sys.stderr)
            print(f"Available fonts: {', '.join(FONT_OPTIONS.keys())}", file=sys.stderr)
            data["font"] = "noto"
        
        language = data.get("language", "en")
        if language not in LANGUAGE_OPTIONS:
            print(f"Warning: Unknown language '{language}'. Using 'en'.", file=sys.stderr)
            print(f"Available languages: {', '.join(LANGUAGE_OPTIONS)}", file=sys.stderr)
            data["language"] = "en"
        
        return data
    
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML syntax: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading YAML file: {e}", file=sys.stderr)
        sys.exit(1)


def build_cv(input_file: Path) -> int:
    """
    Build CV from YAML file using Typst.
    
    Args:
        input_file: Path to the YAML input file
        
    Returns:
        0 on success, 1 on failure
    """
    if not input_file.exists():
        print(f"Error: Input file '{input_file}' not found.", file=sys.stderr)
        return 1
    
    if input_file.suffix.lower() not in ('.yaml', '.yml'):
        print("Error: Input file must be a YAML file (.yaml or .yml)", file=sys.stderr)
        return 1
    
    # Validate YAML content and get data
    data = validate_yaml(input_file)
    
    output_file = input_file.with_suffix('.pdf').resolve()
    
    template_dir = get_template_dir()
    typst_file = template_dir / "main.typ"
    
    if not typst_file.exists():
        print(f"Error: Typst template '{typst_file}' not found.", file=sys.stderr)
        return 1
    
    if not check_typst_installed():
        print("Error: Typst is not installed or not in PATH.", file=sys.stderr)
        print("Install Typst from: https://typst.app/", file=sys.stderr)
        return 1
    
    input_abs = input_file.resolve()
    input_dir = input_abs.parent
    yaml_in_template_dir = template_dir / input_file.name
    
    temp_copy = False
    if input_abs != yaml_in_template_dir:
        shutil.copy2(input_abs, yaml_in_template_dir)
        temp_copy = True
    
    photo_in_template_dir = None
    temp_photo_copy = False
    
    photo_path_str = data.get("photo") if data else None
    
    if photo_path_str is None:
        try:
            with open(input_abs, 'r', encoding='utf-8') as f:
                for line in f:
                    stripped = line.strip()
                    if stripped.startswith("photo:"):
                        photo_path_str = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                        break
        except Exception:
            pass
    
    if photo_path_str:
        photo_path = Path(photo_path_str)
        if not photo_path.is_absolute():
            photo_path = input_dir / photo_path
        
        photo_path = photo_path.resolve()
        
        if photo_path.exists():
            photo_in_template_dir = template_dir / photo_path.name
            if photo_path != photo_in_template_dir.resolve():
                shutil.copy2(photo_path, photo_in_template_dir)
                temp_photo_copy = True
        else:
            print(f"Warning: Photo file '{photo_path_str}' not found.", file=sys.stderr)
    
    print(f"Building CV: {input_file} -> {output_file}")
    
    try:
        result = subprocess.run(
            [
                "typst", "compile",
                "--input", f"cv_data={input_file.name}",
                str(typst_file),
                str(output_file)
            ],
            capture_output=True,
            text=True,
            cwd=str(template_dir)
        )
        
        if temp_copy and yaml_in_template_dir.exists():
            yaml_in_template_dir.unlink()
        if temp_photo_copy and photo_in_template_dir and photo_in_template_dir.exists():
            photo_in_template_dir.unlink()
        
        if result.returncode != 0:
            print("Error: Typst compilation failed:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            return 1
        
        print(f"✓ CV generated successfully: {output_file}")
        return 0
        
    except Exception as e:
        if temp_copy and yaml_in_template_dir.exists():
            yaml_in_template_dir.unlink()
        if temp_photo_copy and photo_in_template_dir and photo_in_template_dir.exists():
            photo_in_template_dir.unlink()
        print(f"Error: {e}", file=sys.stderr)
        return 1


def init_template(output_dir: Path) -> int:
    """
    Initialize a new CV project with template files.
    
    Args:
        output_dir: Directory to create template in
        
    Returns:
        0 on success, 1 on failure
    """
    template_dir = get_template_dir()
    example_yaml = template_dir / "example.yaml"
    
    if not example_yaml.exists():
        print("Error: Example template not found.", file=sys.stderr)
        return 1
    
    output_file = output_dir / "cv.yaml"
    
    if output_file.exists():
        print(f"Error: {output_file} already exists. Remove it first.", file=sys.stderr)
        return 1
    
    shutil.copy2(example_yaml, output_file)
    print(f"✓ Created {output_file}")
    print(f"  Edit this file and run: cvforge {output_file}")
    return 0


def show_fonts():
    """Show available font options."""
    print("Available fonts (all ATS-friendly):\n")
    for key, (primary, fallbacks) in FONT_OPTIONS.items():
        print(f"  {key:12} - {primary}")
    print("\nUsage: Add 'font: <name>' to your cv.yaml file.")


def ats_check(pdf_file: Path) -> int:
    """
    Check if a PDF is ATS-friendly.
    
    Args:
        pdf_file: Path to the PDF file to analyze
        
    Returns:
        0 if ATS-friendly, 1 if issues found
    """
    if not pdf_file.exists():
        print(f"Error: PDF file '{pdf_file}' not found.", file=sys.stderr)
        return 1
    
    if pdf_file.suffix.lower() != '.pdf':
        print("Error: Input file must be a PDF file (.pdf)", file=sys.stderr)
        return 1
    
    if not PYPDF_AVAILABLE:
        print("Error: 'pypdf' library is required for ATS checking.", file=sys.stderr)
        print("Install it with: pip install pypdf", file=sys.stderr)
        return 1
    
    report, output = check_ats(pdf_file)
    print(output)
    
    if report.overall_verdict in ("Excellent", "Good"):
        return 0
    return 1


def main():
    if len(sys.argv) >= 2:
        first_arg = sys.argv[1]
        if (first_arg.lower().endswith('.yaml') or first_arg.lower().endswith('.yml')) and not first_arg.startswith('-'):
            sys.argv.insert(1, "build")
    
    parser = argparse.ArgumentParser(
        prog="cvforge",
        description="Build ATS-friendly CV/Resume from YAML file using Typst.",
        epilog="Examples:\n  cvforge cv.yaml\n  cvforge build resume.yaml\n  cvforge init\n  cvforge fonts\n  cvforge ats-check cv.pdf",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    build_parser = subparsers.add_parser("build", help="Build CV from YAML file")
    build_parser.add_argument(
        "input",
        nargs="?",
        default="cv.yaml",
        help="Input YAML file (default: cv.yaml)"
    )
    
    init_parser = subparsers.add_parser("init", help="Create template cv.yaml")
    init_parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to create template in (default: current directory)"
    )
    
    subparsers.add_parser("fonts", help="Show available font options")
    
    ats_parser = subparsers.add_parser("ats-check", help="Check if PDF is ATS-friendly")
    ats_parser.add_argument(
        "pdf",
        help="PDF file to analyze"
    )
    
    args = parser.parse_args()
    
    if args.command == "init":
        sys.exit(init_template(Path(args.directory)))
    elif args.command == "fonts":
        show_fonts()
        sys.exit(0)
    elif args.command == "build":
        sys.exit(build_cv(Path(args.input)))
    elif args.command == "ats-check":
        sys.exit(ats_check(Path(args.pdf)))
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()

