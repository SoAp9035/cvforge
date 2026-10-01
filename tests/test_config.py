import datetime

import pytest

from cvforge.config import (
    BOLD_END,
    BOLD_START,
    ConfigError,
    normalize_cv,
    render_bold_markers,
)

BASE = {"name": "Ada Lovelace", "role": "Engineer", "email": "ada@example.com"}


def build(**fields):
    return normalize_cv({**BASE, **fields})


def bold(text):
    return f"{BOLD_START}{text}{BOLD_END}"


class TestScalars:
    def test_numbers_and_dates_become_text(self):
        content, _ = build(
            education=[{"school": "Uni", "degree": "BSc", "gpa": 3.36, "date": 2027}],
            experience=[{"company": "X", "role": "Y", "date": datetime.date(2024, 5, 1)}],
            skills=[{"Category": "Years", "Items": ["Python", 2024]}],
            interests=["Chess", 42],
        )
        assert content["education"][0]["gpa"] == "3.36"
        assert content["education"][0]["date"] == "2027"
        assert content["experience"][0]["date"] == "2024-05-01"
        assert content["skills"][0]["items"] == ["Python", "2024"]
        assert content["interests"] == ["Chess", "42"]

    def test_empty_entry_fields_are_dropped(self):
        content, _ = build(projects=[{"name": "P", "date": "", "url": None}])
        assert content["projects"] == [{"name": "P"}]

    def test_nested_mapping_is_rejected(self):
        with pytest.raises(ConfigError, match=r"experience\[1\]\.date"):
            build(experience=[{"company": "X", "date": {"from": 2020}}])


class TestRequiredFields:
    def test_missing_field(self):
        with pytest.raises(ConfigError, match="missing required field 'email'"):
            normalize_cv({"name": "A", "role": "B"})

    def test_blank_field(self):
        with pytest.raises(ConfigError, match="'role' must be non-empty text"):
            build(role="  ")

    @pytest.mark.parametrize("data", [None, {}, ["a"], "text"])
    def test_invalid_document(self, data):
        with pytest.raises(ConfigError):
            normalize_cv(data)

    def test_description_must_be_list(self):
        with pytest.raises(ConfigError, match=r"experience\[1\]\.description"):
            build(experience=[{"company": "X", "description": "one line"}])


class TestBold:
    @pytest.mark.parametrize(
        "source, expected",
        [
            ("Built __fast APIs__ today", f"Built {bold('fast APIs')} today"),
            ("(__bold__).", f"({bold('bold')})."),
            ("my__var__x stays", "my__var__x stays"),
            ("a__b and c__d", "a__b and c__d"),
            ("unmatched __tail", "unmatched __tail"),
            (r"literal \__init\__ here", "literal __init__ here"),
            ("__ spaced __", "__ spaced __"),
            (f"stray {BOLD_START}marker", "stray marker"),
        ],
    )
    def test_markers(self, source, expected):
        assert render_bold_markers(source) == expected

    def test_urls_and_paths_are_untouched(self):
        content, _ = build(
            website="example.com/__x__",
            projects=[{"name": "__P__", "url": "github.com/__u__"}],
        )
        assert content["website"] == "example.com/__x__"
        assert content["projects"][0]["url"] == "github.com/__u__"
        assert content["projects"][0]["name"] == bold("P")


class TestUnknownKeys:
    def test_top_level_typo_warns_with_suggestion(self, capsys):
        content, _ = build(experiance=[{"company": "X"}])
        assert "experiance" not in content
        err = capsys.readouterr().err
        assert "unknown field 'experiance'" in err
        assert "Did you mean 'experience'?" in err

    def test_entry_typo_warns(self, capsys):
        build(experience=[{"company": "X", "descripton": ["a"]}])
        assert "'descripton' in 'experience[1]'" in capsys.readouterr().err


class TestSkills:
    @pytest.mark.parametrize("category, items", [("Category", "Items"), ("category", "items")])
    def test_both_key_styles(self, category, items):
        content, _ = build(skills=[{category: "Lang", items: ["Python"]}])
        assert content["skills"] == [{"category": "Lang", "items": ["Python"]}]

    def test_missing_items(self):
        with pytest.raises(ConfigError, match="missing required field 'items'"):
            build(skills=[{"category": "Lang"}])


class TestSettings:
    def test_defaults(self):
        _, settings = build()
        assert settings["paper"] == "a4"
        assert settings["font-size"] == "10pt"
        assert settings["margin"] == "0.5in"
        assert settings["photo-width"] == "2.5cm"
        assert settings["font-family"][0] == "Noto Sans"
        assert settings["titles"]["skills"] == "Technical Skills"

    def test_layout_overrides(self):
        _, settings = build(paper="letter", **{"font-size": "9.5pt", "margin": "1.5cm"})
        assert settings["paper"] == "us-letter"
        assert settings["font-size"] == "9.5pt"
        assert settings["margin"] == "1.5cm"

    @pytest.mark.parametrize(
        "field, value",
        [("photo-width", "abc"), ("photo-width", "2.5"), ("margin", "1 cm"),
         ("font-size", "12px"), ("font-size", "1cm"), ("paper", "a5")],
    )
    def test_invalid_layout(self, field, value):
        with pytest.raises(ConfigError, match=field):
            build(**{field: value})

    def test_unknown_font_falls_back(self, capsys):
        _, settings = build(font="comic")
        assert settings["font-key"] == "noto"
        assert "unknown font 'comic'" in capsys.readouterr().err

    def test_turkish_titles(self):
        _, settings = build(language="tr")
        assert settings["titles"]["experience"] == "Deneyim"

    def test_custom_titles(self, capsys):
        _, settings = build(
            language="de",
            **{"section-titles": {"experience": "Berufserfahrung", "skils": "x"}},
        )
        assert settings["language"] == "de"
        assert settings["titles"]["experience"] == "Berufserfahrung"
        assert settings["titles"]["education"] == "Education"
        assert "Did you mean 'skills'?" in capsys.readouterr().err

    def test_unknown_language_without_titles_warns(self, capsys):
        _, settings = build(language="de")
        assert settings["titles"]["summary"] == "Summary"
        assert "section-titles" in capsys.readouterr().err

    def test_settings_are_not_rendered_as_content(self):
        content, _ = build(font="times", paper="a4", **{"photo-width": "3cm"})
        assert not {"font", "paper", "photo-width"} & content.keys()


class TestLinks:
    def test_link_text_defaults_to_url(self):
        content, _ = build(github="https://github.com/ada/", linkedin="linkedin.com/in/ada")
        assert content["github-text"] == "github.com/ada"
        assert content["linkedin-text"] == "linkedin.com/in/ada"

    def test_explicit_link_text_is_kept(self):
        content, _ = build(github="github.com/ada", **{"github-text": "GitHub"})
        assert content["github-text"] == "GitHub"
