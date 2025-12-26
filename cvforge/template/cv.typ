// CV Builder - ATS Friendly Typst Template
// Supports dynamic fields, optional photo, Turkish/English, and font selection

#import "@preview/ats-friendly-resume:0.1.1": *

// Get input file path from command line or use default
#let cv_data_path = sys.inputs.at("cv_data", default: "cv.yaml")
#let data = yaml(cv_data_path)

// Helper function to safely get optional fields
#let get(field, default: none) = {
  if field in data { data.at(field) } else { default }
}

// Helper to check if field exists and is not empty
#let has(field) = {
  field in data and data.at(field) != none and data.at(field) != ""
}

// Font mapping - 11 ATS-friendly options
#let font_map = (
  "noto": ("Noto Sans", "DejaVu Sans", "Liberation Sans", "Arial"),
  "roboto": ("Roboto", "Noto Sans", "DejaVu Sans", "Arial"),
  "liberation": ("Liberation Sans", "DejaVu Sans", "Noto Sans", "Arial"),
  "dejavu": ("DejaVu Sans", "Liberation Sans", "Noto Sans", "Arial"),
  "inter": ("Inter", "Noto Sans", "DejaVu Sans", "Arial"),
  // Additional ATS-friendly fonts
  "lato": ("Lato", "Noto Sans", "DejaVu Sans", "Arial"),
  "montserrat": ("Montserrat", "Noto Sans", "DejaVu Sans", "Arial"),
  "raleway": ("Raleway", "Noto Sans", "DejaVu Sans", "Arial"),
  "ubuntu": ("Ubuntu", "Noto Sans", "DejaVu Sans", "Arial"),
  "opensans": ("Open Sans", "Noto Sans", "DejaVu Sans", "Arial"),
  "sourcesans": ("Source Sans Pro", "Noto Sans", "DejaVu Sans", "Arial"),
)

// Get selected font or default to noto
#let selected_font = get("font", default: "noto")
#let font_family = if selected_font in font_map { font_map.at(selected_font) } else { font_map.at("noto") }

// Language configuration
#let lang = get("language", default: "en")

// Section heading translations
#let tr = (
  "en": (
    "summary": "Summary",
    "skills": "Technical Skills",
    "experience": "Experience",
    "education": "Education",
    "projects": "Projects",
    "languages": "Languages",
    "certifications": "Certifications",
    "awards": "Awards",
    "interests": "Interests",
  ),
  "tr": (
    "summary": "Özet",
    "skills": "Teknik Yetenekler",
    "experience": "Deneyim",
    "education": "Eğitim",
    "projects": "Projeler",
    "languages": "Diller",
    "certifications": "Sertifikalar",
    "awards": "Ödüller",
    "interests": "İlgi Alanları",
  ),
)

// Get translation for current language
#let t(key) = {
  let lang_key = if lang in tr { lang } else { "en" }
  tr.at(lang_key).at(key)
}

#show: resume.with(
  author: get("name", default: "Name"),
  author-position: center,
  // Only include optional fields if they exist
  location: get("location", default: none),
  email: get("email", default: none),
  phone: get("phone", default: none),
  linkedin: get("linkedin", default: none),
  github: get("github", default: none),
  portfolio: get("website", default: none),
  personal-info-position: center,
  color-enabled: false,  // ATS-friendly: no colors
  font: font_family,
  paper: "a4",
  author-font-size: 20pt,
  font-size: 10pt,
  lang: lang,
)

// Photo and Role section (if exists)
#if has("photo") or has("role") [
  #align(center)[
    #if has("photo") [
      #box(
        clip: true,
        radius: 4pt,  // Slight rounded corners for professional look
        stroke: 0.5pt + luma(200),
        image(data.photo, width: 2.5cm)  // Width only, height auto for aspect ratio
      )
      #v(0.3em)
    ]
    #if has("role") [
      #text(size: 12pt, style: "italic")[#data.role]
    ]
  ]
  #v(0.5em)
]

// Summary section (if exists)
#if has("summary") [
  == #t("summary")
  #data.summary
]

// Technical Skills section (if exists)
#if has("skills") and data.skills.len() > 0 [
  == #t("skills")
  #for skill in data.skills [
    - *#skill.Category*: #skill.Items.join(", ")
  ]
]

// Experience section (if exists)
#if has("experience") and data.experience.len() > 0 [
  == #t("experience")
  #for job in data.experience [
    #work(
      company: job.at("company", default: ""),
      role: job.at("role", default: ""),
      dates: job.at("date", default: ""),
      location: job.at("location", default: get("location", default: "")),
    )
    #if "description" in job [
      #for bullet in job.description [
        - #bullet
      ]
    ]
  ]
]

// Education section (if exists)
#if has("education") and data.education.len() > 0 [
  == #t("education")
  #for entry in data.education [
    #edu(
      institution: entry.at("school", default: ""),
      degree: entry.at("degree", default: ""),
      dates: entry.at("date", default: ""),
      location: entry.at("location", default: get("location", default: "")),
    )
    #if "description" in entry [
      #for bullet in entry.description [
        - #bullet
      ]
    ]
  ]
]

// Projects section (if exists)
#if has("projects") and data.projects.len() > 0 [
  == #t("projects")
  #for proj in data.projects [
    #project(
      name: proj.at("name", default: ""),
      dates: proj.at("date", default: ""),
      url: proj.at("url", default: none),
    )
    #if "role" in proj [
      #text(style: "italic")[#proj.role]
    ]
    #if "description" in proj [
      #for bullet in proj.description [
        - #bullet
      ]
    ]
  ]
]

// Languages section (if exists)
#if has("languages") and data.languages.len() > 0 [
  == #t("languages")
  #for lang_item in data.languages [
    - *#lang_item.at("name", default: "")*: #lang_item.at("level", default: "")
  ]
]

// Certifications section (if exists)
#if has("certifications") and data.certifications.len() > 0 [
  == #t("certifications")
  #for cert in data.certifications [
    - *#cert.at("name", default: "")* #if "issuer" in cert [(#cert.issuer)] #if "date" in cert [- #cert.date]
  ]
]

// Awards section (if exists)
#if has("awards") and data.awards.len() > 0 [
  == #t("awards")
  #for award in data.awards [
    - *#award.at("name", default: "")* #if "issuer" in award [(#award.issuer)] #if "date" in award [- #award.date]
  ]
]

// Interests section (if exists)
#if has("interests") and data.interests.len() > 0 [
  == #t("interests")
  #data.interests.join(" • ")
]
