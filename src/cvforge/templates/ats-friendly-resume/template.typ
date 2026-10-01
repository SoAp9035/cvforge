// ATS-Friendly Resume Template
// Source: https://github.com/SoAp9035/cvforge
// License: MIT

// Helper function to normalize URLs (avoid double https://)
#let normalize-url(url) = {
  if url.starts-with("https://") or url.starts-with("http://") {
    url
  } else {
    "https://" + url
  }
}

// The CLI marks bold spans with U+E000 (start) and U+E001 (end).
#let render-inline-bold(value) = {
  if type(value) != str or not value.contains("\u{E000}") {
    value
  } else {
    let parts = value.split("\u{E000}")
    let chunks = (parts.first(),)
    for part in parts.slice(1) {
      let pieces = part.split("\u{E001}")
      chunks.push(strong(pieces.first()))
      chunks.push(pieces.slice(1).join(""))
    }
    chunks.join()
  }
}

#let resume(
  // Name of the author (you)
  author: "",
  // Role/Position
  role: "",
  // Photo (optional)
  photo: none,
  photo-width: 2.5cm,
  // Personal Information
  location: "",
  email: "",
  phone: "",
  linkedin: "",
  linkedin-text: "",
  github: "",
  github-text: "",
  website: "",
  website-text: "",
  // Document values and format
  font: "New Computer Modern",
  paper: "a4",
  margin: 0.5in,
  author-font-size: 20pt,
  font-size: 10pt,
  lang: "en",
  body,
) = {
  // Sets document metadata
  set document(author: author, title: author)

  // Hyphenation is off so ATS parsers never see split keywords.
  set text(
    font: font,
    size: font-size,
    lang: lang,
    ligatures: false,
    hyphenate: false,
  )
  set page(
    margin: margin,
    paper: paper,
  )

  show link: set text(fill: blue)
  show link: underline

  // Personal Information
  // display-text: text to show instead of the raw value
  let contact-item(value, link-type: "", display-text: "") = {
    if value != "" {
      let shown-text = if display-text != "" { display-text } else { value }
      if link-type == "https://" {
        link(normalize-url(value))[#shown-text]
      } else if link-type != "" {
        link(link-type + value)[#shown-text]
      } else {
        value
      }
    }
  }

  // Build contact items list
  let contact-items = (
    contact-item(phone),
    contact-item(location),
    contact-item(email, link-type: "mailto:"),
    contact-item(github, link-type: "https://", display-text: github-text),
    contact-item(linkedin, link-type: "https://", display-text: linkedin-text),
    contact-item(website, link-type: "https://", display-text: website-text),
  ).filter(x => x != none)

  let header = [
    #text(weight: "bold", size: author-font-size)[#author]
    #if role != "" [
      #v(0.2em)
      #text(size: 12pt, style: "italic")[#role]
    ]
    #v(0.3em)
    #text(size: font-size)[#contact-items.join("  |  ")]
  ]

  // Header layout: Name, role, and contact on left; photo on right (if provided)
  // ATS-friendly: text is plain and accessible, photo is decorative only
  if photo != none {
    grid(
      columns: (1fr, auto),
      column-gutter: 1em,
      align: (left + horizon, right + horizon),
      header,
      box(
        clip: true,
        radius: 4pt,
        stroke: 0.5pt + luma(200),
        image(photo, width: photo-width),
      ),
    )
  } else {
    // No photo: display header centered for a balanced look
    align(center, header)
  }

  v(0.5em)

  show heading.where(level: 2): it => [
    #pad(top: 0pt, bottom: -10pt, [#smallcaps(it.body)])
    #line(length: 100%, stroke: 1pt)
  ]

  // Main body.
  set par(justify: true)

  body
}

// Components layout template
#let one-by-one-layout(
  left: "",
  right: "",
) = {
  [
    #left #h(1fr) #right
  ]
}

#let two-by-two-layout(
  top-left: "",
  top-right: "",
  bottom-left: "",
  bottom-right: "",
) = {
  [
    #top-left #h(1fr) #top-right \
    #bottom-left #h(1fr) #bottom-right
  ]
}

// Resume components are listed below
// If you want to add some additional components, please make a PR

// Work Component
#let work(
  company: "",
  role: "",
  dates: "",
  location: "",
) = {
  block(spacing: 0.65em)[
    #two-by-two-layout(
      top-left: strong(render-inline-bold(company)),
      top-right: render-inline-bold(dates),
      bottom-left: render-inline-bold(role),
      bottom-right: emph(render-inline-bold(location)),
    )
  ]
}

// Project Component
//
// Optional arguments: url, url-text
#let project(
  name: "",
  dates: "",
  url: "",
  url-text: "",
) = {
  // Use url-text if provided, otherwise fall back to the URL itself
  let display-text = if url-text != "" { url-text } else { url }
  block(spacing: 0.65em)[
    #one-by-one-layout(
      left: [*#render-inline-bold(name)* #if url != "" [(#link(normalize-url(url))[#display-text])]],
      right: render-inline-bold(dates),
    )
  ]
}

// Education Component
//
// Optional arguments: gpa
#let edu(
  institution: "",
  location: "",
  degree: "",
  dates: "",
  gpa: "",
) = {
  block(spacing: 0.65em)[
    #two-by-two-layout(
      top-left: strong(render-inline-bold(institution)),
      top-right: render-inline-bold(location),
      bottom-left: render-inline-bold(if gpa != "" { degree + " | GPA: " + gpa } else { degree }),
      bottom-right: render-inline-bold(dates),
    )
  ]
}
