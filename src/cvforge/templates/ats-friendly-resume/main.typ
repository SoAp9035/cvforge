#import "./template.typ": *

#let cv_data_path = sys.inputs.at("cv_data", default: "cv.yaml")
#let data = yaml(cv_data_path)

#let get(field, default: none) = {
  if field in data { data.at(field) } else { default }
}

#let has(field) = {
  field in data and data.at(field) != none and data.at(field) != ""
}

#let has-text(val) = {
  val != none and val != ""
}

#let has-list(val) = {
  val != none and val.len() > 0
}

#let font_map = (
  "noto": ("Noto Sans", "DejaVu Sans", "Liberation Sans", "Arial"),
  "roboto": ("Roboto", "Noto Sans", "DejaVu Sans", "Arial"),
  "liberation": ("Liberation Sans", "DejaVu Sans", "Noto Sans", "Arial"),
  "dejavu": ("DejaVu Sans", "Liberation Sans", "Noto Sans", "Arial"),
  "inter": ("Inter", "Noto Sans", "DejaVu Sans", "Arial"),
  "lato": ("Lato", "Noto Sans", "DejaVu Sans", "Arial"),
  "montserrat": ("Montserrat", "Noto Sans", "DejaVu Sans", "Arial"),
  "raleway": ("Raleway", "Noto Sans", "DejaVu Sans", "Arial"),
  "ubuntu": ("Ubuntu", "Noto Sans", "DejaVu Sans", "Arial"),
  "opensans": ("Open Sans", "Noto Sans", "DejaVu Sans", "Arial"),
  "sourcesans": ("Source Sans Pro", "Noto Sans", "DejaVu Sans", "Arial"),
  "arial": ("Arial", "Liberation Sans", "Noto Sans", "DejaVu Sans"),
  "times": ("Times New Roman", "Times", "Liberation Serif", "Noto Serif"),
  "calibri": ("Calibri", "Carlito", "Liberation Sans", "Arial"),
  "georgia": ("Georgia", "Gelasio", "Liberation Serif", "Noto Serif"),
  "garamond": ("Garamond", "EB Garamond", "Liberation Serif", "Noto Serif"),
  "trebuchet": ("Trebuchet MS", "Fira Sans", "Liberation Sans", "Arial"),
)

#let selected_font = get("font", default: "noto")
#let font_family = if selected_font in font_map { font_map.at(selected_font) } else { font_map.at("noto") }

#let lang = get("language", default: "en")

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

#let t(key) = {
  let lang_key = if lang in tr { lang } else { "en" }
  tr.at(lang_key).at(key)
}

#show: resume.with(
  author: get("name", default: "Name"),
  author-position: center,
  location: get("location", default: ""),
  email: get("email", default: ""),
  phone: get("phone", default: ""),
  linkedin: get("linkedin", default: ""),
  linkedin-text: get("linkedin-text", default: "LinkedIn"),
  github: get("github", default: ""),
  github-text: get("github-text", default: "GitHub"),
  website: get("website", default: ""),
  website-text: get("website-text", default: "Website"),
  personal-info-position: center,
  color-enabled: false,
  font: font_family,
  paper: "a4",
  author-font-size: 20pt,
  font-size: 10pt,
  lang: lang,
)

#if has("photo") or has("role") [
  #align(center)[
    #if has("photo") [
      #box(
        clip: true,
        radius: 4pt,
        stroke: 0.5pt + luma(200),
        image(data.photo, width: 2.5cm)
      )
      #v(0.3em)
    ]
    #if has("role") [
      #text(size: 12pt, style: "italic")[#data.role]
    ]
  ]
  #v(0.5em)
]

#for (key, val) in data.pairs() {
  if key == "summary" and has-text(val) [
    == #t("summary")
    #val
  ] else if key == "skills" and has-list(val) [
    == #t("skills")
    #for skill in val [
      - *#skill.Category*: #skill.Items.join(", ")
    ]
  ] else if key == "experience" and has-list(val) [
    == #t("experience")
    #for job in val [
      #work(
        company: job.at("company", default: ""),
        role: job.at("role", default: ""),
        dates: job.at("date", default: ""),
        location: job.at("location", default: ""),
      )
      #if "description" in job [
        #for bullet in job.description [
          - #bullet
        ]
      ]
    ]
  ] else if key == "education" and has-list(val) [
    == #t("education")
    #for entry in val [
      #edu(
        institution: entry.at("school", default: ""),
        degree: entry.at("degree", default: ""),
        dates: entry.at("date", default: ""),
        location: entry.at("location", default: ""),
        gpa: entry.at("gpa", default: ""),
      )
      #if "description" in entry [
        #for bullet in entry.description [
          - #bullet
        ]
      ]
    ]
  ] else if key == "projects" and has-list(val) [
    == #t("projects")
    #for proj in val [
      #project(
        name: proj.at("name", default: ""),
        dates: proj.at("date", default: ""),
        url: proj.at("url", default: none),
        url-text: proj.at("url-text", default: ""),
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
  ] else if key == "languages" and has-list(val) [
    == #t("languages")
    #for lang_item in val [
      - *#lang_item.at("name", default: "")*: #lang_item.at("level", default: "")
    ]
  ] else if key == "certifications" and has-list(val) [
    == #t("certifications")
    #for cert in val [
      - *#cert.at("name", default: "")* #if "issuer" in cert [(#cert.issuer)] #if "date" in cert [- #cert.date]
    ]
  ] else if key == "awards" and has-list(val) [
    == #t("awards")
    #for award in val [
      - *#award.at("name", default: "")* #if "issuer" in award [(#award.issuer)] #if "date" in award [- #award.date]
    ]
  ] else if key == "interests" and has-list(val) [
    == #t("interests")
    #val.join(" • ")
  ]
}
