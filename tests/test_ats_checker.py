from pathlib import Path

import pytest

from cvforge import cli
from cvforge.ats_checker import ATSChecker, check_ats


def checker_with_text(text: str) -> ATSChecker:
    checker = ATSChecker(Path("unused.pdf"))
    checker.extracted_text = text
    return checker


class TestStructure:
    def test_aliases_count_once(self):
        result = checker_with_text(
            "Technical Skills\nSkills\nSummary\nProfessional Summary\nExperience\n"
        ).check_structure()
        assert result.passed
        assert "Found 3" in result.message

    def test_words_inside_sentences_do_not_count(self):
        result = checker_with_text(
            "My profile shows skills, education and experience in projects.\n"
        ).check_structure()
        assert not result.passed
        assert result.is_critical

    def test_turkish_and_uppercase_headings(self):
        result = checker_with_text("İLGİ ALANLARI\nDeneyim:\nEĞİTİM\n").check_structure()
        assert "Found 3" in result.message


class TestFonts:
    @pytest.mark.parametrize(
        "font", ["liberationserif-bold", "notosans-regular", "timesnewromanpsmt", "carlito"]
    )
    def test_standard_fonts_pass(self, font, monkeypatch):
        checker = ATSChecker(Path("unused.pdf"))
        monkeypatch.setattr(checker, "get_fonts", lambda: {font})
        assert checker.check_fonts().passed

    def test_non_standard_font_fails_softly(self, monkeypatch):
        checker = ATSChecker(Path("unused.pdf"))
        monkeypatch.setattr(checker, "get_fonts", lambda: {"comicsansms", "arial"})
        result = checker.check_fonts()
        assert not result.passed
        assert result.severity == "warning"
        assert "comicsansms" in result.message
        assert "arial" not in result.message


def test_generated_cv_is_excellent(tmp_path):
    assert cli.init_template(tmp_path) == 0
    assert cli.build_cv(tmp_path / "cv.yaml") == 0
    report, _ = check_ats(tmp_path / "cv.pdf")
    assert report.overall_verdict == "Excellent", [c.message for c in report.checks]
