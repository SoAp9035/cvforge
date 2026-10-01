import sys
import textwrap
from pathlib import Path

import pytest
from pypdf import PdfReader

from cvforge import cli

BASE_YAML = """\
name: "Ada Lovelace"
role: "Engineer"
email: "ada@example.com"
"""


def write_cv(tmp_path: Path, body: str = "", name: str = "cv.yaml") -> Path:
    path = tmp_path / name
    path.write_text(BASE_YAML + textwrap.dedent(body), encoding="utf-8")
    return path


def pdf_text(path: Path) -> str:
    return "\n".join(page.extract_text() for page in PdfReader(str(path)).pages)


def test_build_with_unquoted_numbers(tmp_path):
    cv = write_cv(tmp_path, """
        education:
          - school: "Uni"
            degree: "BSc"
            gpa: 3.36
            date: 2027
        skills:
          - Category: "Years"
            Items: ["Python", 2024]
    """)
    assert cli.build_cv(cv) == 0
    text = pdf_text(tmp_path / "cv.pdf")
    assert "GPA: 3.36" in text
    assert "Python, 2024" in text


def test_credential_date_stays_on_one_line(tmp_path):
    cv = write_cv(tmp_path, """
        certifications:
          - name: "Flutter Bootcamp"
            issuer: "Udemy"
            date: "2026"
        awards:
          - name: "2nd Place"
            date: "2022"
    """)
    assert cli.build_cv(cv) == 0
    text = pdf_text(tmp_path / "cv.pdf")
    assert "Flutter Bootcamp (Udemy) – 2026" in text
    assert "2nd Place – 2022" in text


def test_missing_photo_builds_without_photo(tmp_path, capsys):
    cv = write_cv(tmp_path, 'photo: "missing.jpg"\n')
    assert cli.build_cv(cv) == 0
    assert "building without a photo" in capsys.readouterr().err
    assert (tmp_path / "cv.pdf").exists()


def test_invalid_photo_width_fails_before_typst(tmp_path, capsys):
    cv = write_cv(tmp_path, 'photo-width: "abc"\n')
    assert cli.build_cv(cv) == 1
    assert "'photo-width' must be a length" in capsys.readouterr().err
    assert not (tmp_path / "cv.pdf").exists()


def test_links_show_urls_for_ats(tmp_path):
    cv = write_cv(tmp_path, 'github: "github.com/ada"\nlinkedin: "linkedin.com/in/ada"\n')
    assert cli.build_cv(cv) == 0
    text = pdf_text(tmp_path / "cv.pdf")
    assert "github.com/ada" in text
    assert "linkedin.com/in/ada" in text


def test_bold_escape_renders_literal_underscores(tmp_path):
    cv = write_cv(tmp_path, "summary: 'Wrote \\__init\\__ and __bold__ text.'\n")
    assert cli.build_cv(cv) == 0
    assert "Wrote __init__ and bold text." in pdf_text(tmp_path / "cv.pdf")


def test_no_hyphenation(tmp_path):
    long_words = " ".join(["geliştirilebilirlik uluslararasılaştırma"] * 30)
    cv = write_cv(tmp_path, f'language: "tr"\nsummary: "{long_words}"\n')
    assert cli.build_cv(cv) == 0
    for line in pdf_text(tmp_path / "cv.pdf").splitlines():
        assert not line.rstrip().endswith(("-", "­")), line


def test_section_titles_and_order(tmp_path):
    cv = write_cv(tmp_path, """
        language: "de"
        section-titles:
          experience: "Berufserfahrung"
        experience:
          - company: "X"
            role: "Y"
        summary: "Later section."
    """)
    assert cli.build_cv(cv) == 0
    text = pdf_text(tmp_path / "cv.pdf")
    assert text.index("Berufserfahrung") < text.index("Summary")


@pytest.mark.parametrize("paper, width", [("a4", 595), ("letter", 612)])
def test_paper_size(tmp_path, paper, width):
    cv = write_cv(tmp_path, f'paper: "{paper}"\n')
    assert cli.build_cv(cv) == 0
    page = PdfReader(str(tmp_path / "cv.pdf")).pages[0]
    assert round(float(page.mediabox.width)) == width


def test_output_option(tmp_path):
    cv = write_cv(tmp_path)
    out = tmp_path / "out" / "nested" / "resume.pdf"
    assert cli.build_cv(cv, out) == 0
    assert out.exists()
    assert not (tmp_path / "cv.pdf").exists()


def test_output_directory(tmp_path):
    cv = write_cv(tmp_path)
    out_dir = tmp_path / "dist"
    out_dir.mkdir()
    assert cli.build_cv(cv, out_dir) == 0
    assert (out_dir / "cv.pdf").exists()


def test_output_must_be_pdf(tmp_path, capsys):
    cv = write_cv(tmp_path)
    assert cli.build_cv(cv, tmp_path / "resume.txt") == 1
    assert "must end with .pdf" in capsys.readouterr().err


def test_invalid_yaml_syntax(tmp_path, capsys):
    cv = tmp_path / "cv.yaml"
    cv.write_text("name: [unclosed\n", encoding="utf-8")
    assert cli.build_cv(cv) == 1
    assert "invalid YAML syntax" in capsys.readouterr().err


def test_cli_shortcut_with_output(tmp_path, monkeypatch):
    cv = write_cv(tmp_path)
    out = tmp_path / "x.pdf"
    monkeypatch.setattr(sys, "argv", ["cvforge", str(cv), "-o", str(out)])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 0
    assert out.exists()


def test_init_example_builds(tmp_path):
    assert cli.init_template(tmp_path) == 0
    assert cli.build_cv(tmp_path / "cv.yaml") == 0
