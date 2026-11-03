#import "@local/mirea_title_list:1.0.0": titlepage
#import "@local/gost:1.0.0": gost

#let discipline = "Инструменты девопс"
#let student = "Бунто М. В."
#let group = none
#let teacher = "Гиматдинов Д. М."
#let teacher-position = "ст. преп."
#let year = 2026

#let shot(title, cmd, path, caption: none) = {
  heading(level: 2, title)
  if cmd != none {
    block(width: 100%, inset: 6pt, fill: luma(245), stroke: 0.4pt + luma(200))[
      #text(font: ("DejaVu Sans Mono", "Liberation Mono"), size: 8.5pt)[#cmd]
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
