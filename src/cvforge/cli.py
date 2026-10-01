#!/usr/bin/env python3
"""
CVForge CLI - Build ATS-friendly CVs from YAML using Typst.
"""

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

import typst
import yaml

from . import __version__
from .ats_checker import check_ats
from .config import FONT_OPTIONS, ConfigError, load_cv

DEFAULT_TEMPLATE = "ats-friendly-resume"


def get_templates_dir() -> Path:
    """Get the path to the templates directory."""
    return Path(__file__).parent / "templates"


def get_template_dir(template_name: str = DEFAULT_TEMPLATE) -> Path:
    """Get the path to a specific template directory."""
    return get_templates_dir() / template_name


def resolve_output(input_file: Path, output: Path | None) -> Path | None:
    if output is None:
        return input_file.with_suffix(".pdf").resolve()
    if output.is_dir():
        return (output / input_file.with_suffix(".pdf").name).resolve()
    if output.suffix.lower() != ".pdf":
        print("Error: Output file must end with .pdf", file=sys.stderr)
        return None
    output.parent.mkdir(parents=True, exist_ok=True)
    return output.resolve()


def installed_font_families() -> set[str]:
    try:
        return {name.lower() for name in typst.Fonts().families()}
    except Exception:
        return set()


def warn_missing_font(settings: dict) -> None:
    families = settings["font-family"]
    installed = installed_font_families()
    if not installed or families[0].lower() in installed:
        return
    fallback = next((f for f in families[1:] if f.lower() in installed), None)
    used = f"'{fallback}'" if fallback else "Typst's built-in default font"
    print(
        f"Warning: font '{families[0]}' (font: {settings['font-key']}) is not installed; "
        f"using {used} instead.",
        file=sys.stderr,
    )


def copy_photo(content: dict, input_dir: Path, build_dir: Path) -> None:
    """Copy the photo next to the template, or drop it with a warning."""
    photo = content.get("photo")
    if not photo:
        return

    photo_path = Path(photo)
    if not photo_path.is_absolute():
        photo_path = input_dir / photo_path
    photo_path = photo_path.resolve()

    if not photo_path.is_file():
        print(
            f"Warning: photo file '{photo}' not found; building without a photo.",
            file=sys.stderr,
        )
        del content["photo"]
        return

    target = build_dir / f"cvforge-photo{photo_path.suffix.lower()}"
    shutil.copy2(photo_path, target)
    content["photo"] = target.name


def write_yaml(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def build_cv(input_file: Path, output: Path | None = None) -> int:
    """
    Build CV from YAML file using Typst.
    
    Args:
        input_file: Path to the YAML input file
        output: Optional output PDF path or directory
        
    Returns:
        0 on success, 1 on failure
    """
    if not input_file.exists():
        print(f"Error: Input file '{input_file}' not found.", file=sys.stderr)
        return 1
    
    if input_file.suffix.lower() not in ('.yaml', '.yml'):
        print("Error: Input file must be a YAML file (.yaml or .yml)", file=sys.stderr)
        return 1

    try:
        content, settings = load_cv(input_file)
    except ConfigError as e:
        print(f"Error: Invalid YAML: {e}", file=sys.stderr)
        return 1

    output_file = resolve_output(input_file, output)
    if output_file is None:
        return 1

    template_dir = get_template_dir()
    if not (template_dir / "main.typ").exists():
        print(f"Error: Typst template '{template_dir / 'main.typ'}' not found.", file=sys.stderr)
        return 1

    print(f"Building CV: {input_file} -> {output_file}", flush=True)
    warn_missing_font(settings)

    try:
        with tempfile.TemporaryDirectory(prefix="cvforge-") as build_dir_name:
            build_dir = Path(build_dir_name) / template_dir.name
            shutil.copytree(template_dir, build_dir)

            copy_photo(content, input_file.resolve().parent, build_dir)
            write_yaml(build_dir / "cvforge-data.yaml", content)
            write_yaml(build_dir / "cvforge-settings.yaml", settings)

            _, warnings = typst.compile_with_warnings(
                input=str(build_dir / "main.typ"),
                output=str(output_file),
                root=str(build_dir),
            )
            for warning in warnings:
                # Font fallbacks are reported once by warn_missing_font.
                if not warning.message.startswith("unknown font family"):
                    print(f"Warning: Typst: {warning.message}", file=sys.stderr)

        print(f"✓ CV generated successfully: {output_file}")
        return 0

    except Exception as e:
        print("Error: Typst compilation failed:", file=sys.stderr)
        print(f"  {e}", file=sys.stderr)
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

    output_dir = output_dir.resolve()
    if output_dir.exists() and not output_dir.is_dir():
        print(f"Error: {output_dir} is not a directory.", file=sys.stderr)
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    
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
    for key, families in FONT_OPTIONS.items():
        print(f"  {key:12} - {families[0]}")
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
        description="Build clean, ATS-friendly PDF resumes from YAML with Typst.",
        epilog="Examples:\n  cvforge init\n  cvforge cv.yaml\n  cvforge build resume.yaml -o out/resume.pdf\n  cvforge fonts\n  cvforge ats-check cv.pdf",
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
    build_parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output PDF path or directory (default: next to the YAML file)"
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
        sys.exit(build_cv(Path(args.input), args.output))
    elif args.command == "ats-check":
        sys.exit(ats_check(Path(args.pdf)))
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
