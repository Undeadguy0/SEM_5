#let student = "Михаил"
#let discipline = "Инструменты DevOps"
#let date = "2026-10-27"

#let setup() = {
  set page(paper: "a4", margin: 2cm)
  set text(font: "DejaVu Sans", size: 11pt, lang: "ru")
  set heading(numbering: "1.")
  show raw: set text(font: "DejaVu Sans Mono", size: 8.5pt)
  show figure.caption: set text(size: 9pt)
}

#let title-page(lab-num, theme) = {
  align(center)[
    #v(2.5cm)
    #text(14pt, weight: "bold")[МИРЭА — Российский технологический университет]
    #v(0.4cm)
    #text(12pt)[Институт ИПТИП · Кафедра индустриального программирования]
    #v(2cm)
    #text(16pt, weight: "bold")[#lab-num]
    #v(0.6cm)
    #text(13pt)[#theme]
    #v(2cm)
    #align(left)[
      #pad(left: 2cm)[
        *Студент:* #student \
        *Дисциплина:* #discipline \
        *Дата отчёта:* #date \
        *ВМ:* devops-vm (VirtualBox) \
        *Доступ:* SSH NAT `127.0.0.1:2222` (`ssh devops`)
      ]
    ]
    #v(1fr)
    #text(10pt)[Проверки зафиксированы как терминальные снимки (PNG) вывода команд.]
  ]
  pagebreak()
}

#let shot(title, cmd, path, caption: none) = {
  heading(level: 2, title)
  if cmd != none {
    block(width: 100%, inset: 6pt, fill: luma(245), stroke: 0.4pt + luma(200))[
      #text(font: "DejaVu Sans Mono", size: 8.5pt)[#cmd]
    ]
  }
  v(0.25cm)
  image(path, width: 100%)
  if caption != none {
    v(0.15cm)
    text(9pt, fill: luma(80))[#caption]
  }
  v(0.4cm)
}
