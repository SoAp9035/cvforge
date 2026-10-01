#import "./template.typ": *

// Both files are written by the CVForge CLI after validation, so every
// content value here is text and inline-bold markers are already resolved.
#let data = yaml(sys.inputs.at("cv_data", default: "cvforge-data.yaml"))
#let settings = yaml(sys.inputs.at("cv_settings", default: "cvforge-settings.yaml"))

#let get(field, default: "") = {
  if field in data { data.at(field) } else { default }
}

#let t(key) = settings.titles.at(key)

#show: resume.with(
  author: get("name"),
  role: get("role"),
  photo: if "photo" in data { data.photo } else { none },
  photo-width: eval(settings.at("photo-width")),
  location: get("location"),
  email: get("email"),
  phone: get("phone"),
  linkedin: get("linkedin"),
  linkedin-text: get("linkedin-text"),
  github: get("github"),
  github-text: get("github-text"),
  website: get("website"),
  website-text: get("website-text"),
  font: settings.at("font-family"),
  paper: settings.paper,
  margin: eval(settings.margin),
  font-size: eval(settings.at("font-size")),
  lang: settings.language,
)

// Name, then optional " (issuer)" and " – date", for certifications and awards.
#let credential(entry) = {
  strong(render-inline-bold(entry.at("name", default: "")))
  if "issuer" in entry [ (#render-inline-bold(entry.issuer))]
  if "date" in entry [ – #render-inline-bold(entry.date)]
}

#let bullets(entry) = {
  for bullet in entry.at("description", default: ()) [
    - #render-inline-bold(bullet)
  ]
}

#for (key, val) in data.pairs() {
  if key == "summary" [
    == #t("summary")
    #render-inline-bold(val)
  ] else if key == "skills" [
    == #t("skills")
    #for skill in val [
      - *#render-inline-bold(skill.category)*: #render-inline-bold(skill.items.join(", "))
    ]
  ] else if key == "experience" [
    == #t("experience")
    #for job in val [
      #work(
        company: job.at("company", default: ""),
        role: job.at("role", default: ""),
        dates: job.at("date", default: ""),
        location: job.at("location", default: ""),
      )
      #bullets(job)
    ]
  ] else if key == "education" [
    == #t("education")
    #for entry in val [
      #edu(
        institution: entry.at("school", default: ""),
        degree: entry.at("degree", default: ""),
        dates: entry.at("date", default: ""),
        location: entry.at("location", default: ""),
        gpa: entry.at("gpa", default: ""),
      )
      #bullets(entry)
    ]
  ] else if key == "projects" [
    == #t("projects")
    #for proj in val [
      #project(
        name: proj.at("name", default: ""),
        dates: proj.at("date", default: ""),
        url: proj.at("url", default: ""),
        url-text: proj.at("url-text", default: ""),
      )
      #if "role" in proj [
        #text(style: "italic")[#render-inline-bold(proj.role)]
      ]
      #bullets(proj)
    ]
  ] else if key == "languages" [
    == #t("languages")
    #for lang_item in val [
      - *#render-inline-bold(lang_item.at("name", default: ""))*#if "level" in lang_item [: #render-inline-bold(lang_item.level)]
    ]
  ] else if key == "certifications" [
    == #t("certifications")
    #for cert in val [
      - #credential(cert)
    ]
  ] else if key == "awards" [
    == #t("awards")
    #for award in val [
      - #credential(award)
    ]
  ] else if key == "interests" [
    == #t("interests")
    #val.map(render-inline-bold).join(" • ")
  ]
}
