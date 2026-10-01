"""
CV YAML validation and normalization for CVForge.

Everything the Typst template needs is prepared here, so the template only
renders data that is already known to be well-formed text.
"""

import datetime
import difflib
import re
import sys
from pathlib import Path

import yaml

# Font keys map to a family chain: the first installed family is used.
FONT_OPTIONS = {
    "noto": ["Noto Sans", "DejaVu Sans", "Liberation Sans", "Arial"],
    "roboto": ["Roboto", "Noto Sans", "DejaVu Sans", "Arial"],
    "liberation": ["Liberation Sans", "DejaVu Sans", "Noto Sans", "Arial"],
    "dejavu": ["DejaVu Sans", "Liberation Sans", "Noto Sans", "Arial"],
    "inter": ["Inter", "Noto Sans", "DejaVu Sans", "Arial"],
    "lato": ["Lato", "Noto Sans", "DejaVu Sans", "Arial"],
    "montserrat": ["Montserrat", "Noto Sans", "DejaVu Sans", "Arial"],
    "raleway": ["Raleway", "Noto Sans", "DejaVu Sans", "Arial"],
    "ubuntu": ["Ubuntu", "Noto Sans", "DejaVu Sans", "Arial"],
    "opensans": ["Open Sans", "Noto Sans", "DejaVu Sans", "Arial"],
    "sourcesans": ["Source Sans Pro", "Noto Sans", "DejaVu Sans", "Arial"],
    "arial": ["Arial", "Liberation Sans", "Noto Sans", "DejaVu Sans"],
    "times": ["Times New Roman", "Times", "Liberation Serif", "Noto Serif"],
    "calibri": ["Calibri", "Carlito", "Liberation Sans", "Arial"],
    "georgia": ["Georgia", "Gelasio", "Liberation Serif", "Noto Serif"],
    "garamond": ["Garamond", "EB Garamond", "Liberation Serif", "Noto Serif"],
    "trebuchet": ["Trebuchet MS", "Fira Sans", "Liberation Sans", "Arial"],
}
DEFAULT_FONT = "noto"

SECTION_TITLES = {
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
DEFAULT_LANGUAGE = "en"
LANGUAGE_RE = re.compile(r"^[a-z]{2,3}$")

PAPER_OPTIONS = {"a4": "a4", "us-letter": "us-letter", "letter": "us-letter"}
DEFAULT_LAYOUT = {
    "paper": "a4",
    "font-size": "10pt",
    "margin": "0.5in",
    "photo-width": "2.5cm",
}
LENGTH_RE = re.compile(r"^\d+(\.\d+)?(pt|mm|cm|in)$")
FONT_SIZE_RE = re.compile(r"^\d+(\.\d+)?pt$")

REQUIRED_IDENTITY_FIELDS = ("name", "role", "email")
LINK_FIELDS = ("website", "linkedin", "github")

SETTING_FIELDS = (
    "language", "font", "paper", "font-size", "margin", "section-titles",
)
IDENTITY_FIELDS = (
    "name", "role", "email", "phone", "location",
    "website", "website-text", "linkedin", "linkedin-text",
    "github", "github-text", "photo", "photo-width",
)
SECTION_FIELDS = {
    "experience": ("company", "role", "date", "location", "description"),
    "education": ("school", "degree", "date", "location", "gpa", "description"),
    "projects": ("name", "date", "url", "url-text", "role", "description"),
    "certifications": ("name", "issuer", "date"),
    "awards": ("name", "issuer", "date"),
    "languages": ("name", "level"),
}
BULLET_SECTIONS = ("experience", "education", "projects")
KNOWN_TOP_LEVEL = (
    SETTING_FIELDS + IDENTITY_FIELDS
    + ("summary", "skills", "interests")
    + tuple(SECTION_FIELDS)
)

# Values that are paths, URLs or settings never get inline-bold processing.
NON_NARRATIVE_FIELDS = {
    "email", "phone", "website", "linkedin", "github", "photo", "photo-width",
    "url", "language", "font", "paper", "font-size", "margin",
}

# Private-use characters mark bold spans for the Typst template.
BOLD_START = ""
BOLD_END = ""
# Opening "__" must not follow a word character and closing "__" must not
# precede one, so identifiers such as my__var stay literal. "\__" is literal.
BOLD_RE = re.compile(r"(?<![\w\\])__(?=\S)(.+?)(?<=\S)(?<!\\)__(?!\w)")


class ConfigError(Exception):
    """Raised when the CV YAML cannot be built."""


def warn(message: str) -> None:
    print(f"Warning: {message}", file=sys.stderr)


def type_name(value) -> str:
    return type(value).__name__


def is_empty(value) -> bool:
    return value is None or value == ""


def to_text(value):
    """Convert YAML scalars (numbers, dates, booleans) to text."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float, datetime.date)):
        return str(value)
    return value


def render_bold_markers(text: str) -> str:
    text = text.replace(BOLD_START, "").replace(BOLD_END, "")
    text = BOLD_RE.sub(lambda m: BOLD_START + m.group(1) + BOLD_END, text)
    return text.replace("\\__", "__")


def display_url(url: str) -> str:
    """Strip the scheme and trailing slash so the visible text is the URL."""
    return re.sub(r"^https?://", "", url).rstrip("/")


def warn_unknown_keys(keys, known, where: str) -> None:
    for key in keys:
        if key in known:
            continue
        message = f"unknown field '{key}' in {where} is ignored."
        suggestion = difflib.get_close_matches(key, known, n=1)
        if suggestion:
            message += f" Did you mean '{suggestion[0]}'?"
        warn(message)


def require_text(value, where: str) -> str:
    value = to_text(value)
    if not isinstance(value, str):
        raise ConfigError(f"'{where}' must be text, not {type_name(value)}.")
    return value


def normalize_text_list(value, where: str) -> list:
    if not isinstance(value, list):
        raise ConfigError(f"'{where}' must be a list, not {type_name(value)}.")
    return [require_text(item, f"{where}[{i}]") for i, item in enumerate(value, start=1)]


def normalize_skills(value) -> list:
    if not isinstance(value, list):
        raise ConfigError(
            f"'skills' must be a list of skill groups, not {type_name(value)}."
        )

    groups = []
    for index, skill in enumerate(value, start=1):
        where = f"skills[{index}]"
        if not isinstance(skill, dict):
            raise ConfigError(f"'{where}' must be a mapping, not {type_name(skill)}.")

        # Capitalized keys are the original format and remain supported.
        lowered = {}
        for key, item in skill.items():
            canonical = key.lower() if key in ("Category", "Items") else key
            lowered[canonical] = item
        warn_unknown_keys(lowered, ("category", "items"), f"'{where}'")

        for field in ("category", "items"):
            if field not in lowered:
                raise ConfigError(f"'{where}' is missing required field '{field}'.")

        groups.append({
            "category": require_text(lowered["category"], f"{where}.category"),
            "items": normalize_text_list(lowered["items"], f"{where}.items"),
        })
    return groups


def normalize_entries(section: str, value) -> list:
    if not isinstance(value, list):
        raise ConfigError(f"'{section}' must be a list, not {type_name(value)}.")

    fields = SECTION_FIELDS[section]
    entries = []
    for index, item in enumerate(value, start=1):
        where = f"{section}[{index}]"
        if not isinstance(item, dict):
            raise ConfigError(f"'{where}' must be a mapping, not {type_name(item)}.")
        warn_unknown_keys(item, fields, f"'{where}'")

        entry = {}
        for field in fields:
            field_value = item.get(field)
            if is_empty(field_value):
                continue
            if field == "description":
                entry[field] = normalize_text_list(field_value, f"{where}.description")
            else:
                entry[field] = require_text(field_value, f"{where}.{field}")
        entries.append(entry)
    return entries


def normalize_length(data: dict, field: str, pattern: re.Pattern, example: str) -> str:
    value = data.get(field)
    if is_empty(value):
        return DEFAULT_LAYOUT[field]
    value = require_text(value, field).strip()
    if not pattern.match(value):
        raise ConfigError(
            f"'{field}' must be a length such as \"{example}\", not \"{value}\"."
        )
    return value


def normalize_settings(data: dict) -> dict:
    font = data.get("font", DEFAULT_FONT)
    if font not in FONT_OPTIONS:
        warn(f"unknown font '{font}'. Using '{DEFAULT_FONT}'.")
        print(f"Available fonts: {', '.join(FONT_OPTIONS)}", file=sys.stderr)
        font = DEFAULT_FONT

    language = to_text(data.get("language", DEFAULT_LANGUAGE))
    if not isinstance(language, str) or not LANGUAGE_RE.match(language):
        warn(f"invalid language '{language}'. Using '{DEFAULT_LANGUAGE}'.")
        language = DEFAULT_LANGUAGE

    titles = dict(SECTION_TITLES.get(language, SECTION_TITLES[DEFAULT_LANGUAGE]))
    custom_titles = data.get("section-titles")
    if not is_empty(custom_titles):
        if not isinstance(custom_titles, dict):
            raise ConfigError(
                f"'section-titles' must be a mapping, not {type_name(custom_titles)}."
            )
        warn_unknown_keys(custom_titles, tuple(titles), "'section-titles'")
        for key, title in custom_titles.items():
            if key in titles:
                title = require_text(title, f"section-titles.{key}")
                if not title.strip():
                    raise ConfigError(f"'section-titles.{key}' must be non-empty text.")
                titles[key] = title
    elif language not in SECTION_TITLES:
        warn(
            f"no built-in section headings for language '{language}'; using English. "
            "Translate them with 'section-titles'."
        )

    paper = to_text(data.get("paper", DEFAULT_LAYOUT["paper"]))
    if paper not in PAPER_OPTIONS:
        raise ConfigError(
            f"'paper' must be one of {', '.join(sorted(PAPER_OPTIONS))}, not \"{paper}\"."
        )

    return {
        "language": language,
        "font-key": font,
        "font-family": FONT_OPTIONS[font],
        "titles": titles,
        "paper": PAPER_OPTIONS[paper],
        "font-size": normalize_length(data, "font-size", FONT_SIZE_RE, "10pt"),
        "margin": normalize_length(data, "margin", LENGTH_RE, "0.5in"),
        "photo-width": normalize_length(data, "photo-width", LENGTH_RE, "2.5cm"),
    }


def apply_bold(value, key=None):
    if isinstance(value, str):
        return value if key in NON_NARRATIVE_FIELDS else render_bold_markers(value)
    if isinstance(value, list):
        return [apply_bold(item, key) for item in value]
    if isinstance(value, dict):
        return {k: apply_bold(v, k) for k, v in value.items()}
    return value


def normalize_cv(data) -> tuple[dict, dict]:
    """
    Validate parsed YAML and return (content, settings).

    Content keeps the YAML section order, contains only text values, and has
    inline-bold markers applied. Settings hold layout and font choices.
    """
    if data is None or data == {}:
        raise ConfigError("YAML file is empty.")
    if not isinstance(data, dict):
        raise ConfigError(f"top-level document must be a mapping, not {type_name(data)}.")

    warn_unknown_keys(data, KNOWN_TOP_LEVEL, "the top level")

    for field in REQUIRED_IDENTITY_FIELDS:
        if field not in data:
            raise ConfigError(f"missing required field '{field}'.")
        value = to_text(data[field])
        if not isinstance(value, str) or not value.strip():
            raise ConfigError(f"'{field}' must be non-empty text.")

    settings = normalize_settings(data)

    content = {}
    for key, value in data.items():
        if key in SETTING_FIELDS or key == "photo-width" or key not in KNOWN_TOP_LEVEL:
            continue
        if is_empty(value):
            continue
        if key == "skills":
            content[key] = normalize_skills(value)
        elif key in SECTION_FIELDS:
            content[key] = normalize_entries(key, value)
        elif key == "interests":
            content[key] = normalize_text_list(value, "interests")
        else:
            content[key] = require_text(value, key)

    for field in LINK_FIELDS:
        text_field = f"{field}-text"
        if field in content and text_field not in content:
            content[text_field] = display_url(content[field])

    return apply_bold(content), settings


def load_cv(yaml_path: Path) -> tuple[dict, dict]:
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigError(f"invalid YAML syntax: {e}") from e
    except OSError as e:
        raise ConfigError(f"could not read YAML file: {e}") from e
    return normalize_cv(data)
