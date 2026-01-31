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

#let resume(
  // Name of the author (you)
  author: "",
  author-position: left,
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
  linkedin-text: "LinkedIn",
  github: "",
  github-text: "GitHub",
  website: "",
  website-text: "Website",
  personal-info-position: left,
  // Document values and format
  color-enabled: true,
  text-color: "#000080",
  font: "New Computer Modern",
  paper: "us-letter",
  author-font-size: 20pt,
  font-size: 10pt,
  lang: "en",
  body,
) = {
  // Sets document metadata
  set document(author: author, title: author)

  // Document-wide formatting, including font and margins
  set text(
    font: font,
    size: font-size,
    lang: lang,
    ligatures: false,
  )
  set page(
    margin: 0.5in,
    paper: paper,
  )

  // Accent Color Styling
  show heading: set text(fill: if color-enabled { rgb(text-color) } else { black })
  show link: set text(fill: if color-enabled { rgb(text-color) } else { blue })

  // Link styles
  show link: underline

  // Personal Information
  // display-text: optional text to show instead of the raw URL
  let contact-item(value, prefix: "", link-type: "", display-text: "") = {
    if value != "" {
      if link-type != "" {
        // Use display-text if provided, otherwise fall back to the value
        let shown-text = if display-text != "" { display-text } else { value }
        if link-type == "https://" {
          link(normalize-url(value))[#shown-text]
        } else {
          link(link-type + value)[#(prefix + shown-text)]
        }
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

  // Header layout: Name, role, and contact on left; photo on right (if provided)
  // ATS-friendly: text is plain and accessible, photo is decorative only
  if photo != none {
    grid(
      columns: (1fr, auto),
      column-gutter: 1em,
      align: (left + horizon, right + horizon),
      [
        #text(weight: "bold", size: author-font-size, fill: if color-enabled { rgb(text-color) } else { black })[#author]
        #if role != "" [
          #v(0.2em)
          #text(size: 12pt, style: "italic")[#role]
        ]
        #v(0.3em)
        #text(size: font-size)[#contact-items.join("  |  ")]
      ],
      [
        #box(
          clip: true,
          radius: 4pt,
          stroke: 0.5pt + luma(200),
          image(photo, width: photo-width)
        )
      ],
    )
  } else {
    // No photo: display header centered for a balanced look
    align(center)[
      #text(weight: "bold", size: author-font-size, fill: if color-enabled { rgb(text-color) } else { black })[#author]
      #if role != "" [
        #v(0.2em)
        #text(size: 12pt, style: "italic")[#role]
      ]
      #v(0.3em)
      #text(size: font-size)[#contact-items.join("  |  ")]
    ]
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

// Dates that can be use for components
//
// Example:
//
// Sep 2021 - Aug 2025 (end date is defined)
//
// Sep 2021 (if no end date defined)
#let dates-util(
  start-date: "",
  end-date: "",
) = {
  if end-date == "" {
    start-date
  } else {
    start-date + " " + $dash.em$ + " " + end-date
  }
}

// Resume components are listed below
// If you want to add some additional components, please make a PR

// Work Component
//
// Optional arguments: tech-used
#let work(
  company: "",
  role: "",
  dates: "",
  tech-used: "",
  location: "",
) = {
  block(spacing: 0.65em)[
    #if tech-used == "" [
      #two-by-two-layout(
        top-left: strong(company),
        top-right: dates,
        bottom-left: role,
        bottom-right: emph(location),
      )
    ] else [
      #two-by-two-layout(
        top-left: strong(company) + " " + "|" + " " + strong(role),
        top-right: dates,
        bottom-left: tech-used,
        bottom-right: emph(location),
      )
    ]
  ]
}

// Project Component
//
// Optional arguments: tech-used, url-text
#let project(
  name: "",
  dates: "",
  tech-used: "",
  url: "",
  url-text: "",
) = {
  // Use url-text if provided, otherwise fall back to the URL itself
  let display-text = if url-text != "" { url-text } else { url }
  block(spacing: 0.65em)[
    #if tech-used == "" [
      #one-by-one-layout(
        left: [*#name* #if url != "" and url != none [(#link(normalize-url(url))[#display-text])]],
        right: dates,
      )
    ] else [
      #two-by-two-layout(
        top-left: strong(name),
        top-right: dates,
        bottom-left: tech-used,
        bottom-right: if url != "" and url != none [(#link(normalize-url(url))[#display-text])] else [],
      )
    ]
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
      top-left: strong(institution),
      top-right: location,
      bottom-left: if gpa != "" { degree + " | GPA: " + gpa } else { degree },
      bottom-right: dates,
    )
  ]
}
