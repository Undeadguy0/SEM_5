#import "common.typ": *

// Keep each check (heading + command + screenshot + caption) on one page.
#let shot(title, cmd, path, caption: none) = {
  block(breakable: false)[
    #heading(level: 2, title)
    #if cmd != none {
      block(width: 100%, inset: 6pt, fill: luma(245), stroke: 0.4pt + luma(200))[
        #text(font: ("DejaVu Sans Mono", "Liberation Mono"), size: 8.5pt)[#cmd]
      ]
    }
    #v(0.25cm)
    #image(path, width: 100%)
    #if caption != none {
      v(0.15cm)
      text(9pt, fill: luma(80))[#caption]
    }
    #v(0.4cm)
  ]
}

#titlepage(
  work-type: "Практическая работа",
  number: "5.1",
  discipline: discipline,
  topic: "Создание веб-сайта с использованием GitHub Pages",
  group: group,
  student: student,
  teacher-position: teacher-position,
  teacher: teacher,
  year: year,
)

#show: gost.with(profile: "mirea")
#pagebreak()

= Цель отчёта
Подтверждение репозитория `Undeadguy0.github.io`, публикации через GitHub Actions
(Jekyll), наличия `README.md` и статической страницы `hello.html`, успешного
pipeline и доступности сайта.

= Проверки

#shot(
  "1. Репозиторий и remote",
  `git remote -v`,
  "shots/pr51/t51-01-remote.png",
  caption: [Репозиторий `github.com/Undeadguy0/Undeadguy0.github.io`.],
)

#shot(
  "2. История коммитов",
  `git log --oneline --decorate -5`,
  "shots/pr51/t51-02-log.png",
  caption: [Рабочий коммит `59c4491` на `origin/master` и `origin/main`. Деплой идёт с default-ветки `master`.],
)

#shot(
  "3. Состав репозитория",
  `git ls-files`,
  "shots/pr51/t51-03-tree.png",
  caption: [Есть `README.md`, `hello.html`, `.github/workflows/deploy.yml`. Сохранена существующая Jekyll-визитка.],
)

#shot(
  "4. Статическая страница hello.html",
  `type hello.html`,
  "shots/pr51/t51-04-hello.png",
  caption: [Страница «Hello, GitHub Actions!», title «GitHub Deployment Workflow».],
)

#shot(
  "5. Workflow deploy.yml",
  `type .github/workflows/deploy.yml`,
  "shots/pr51/t51-05-workflow.png",
  caption: [Триггер: `push` в `master` и `workflow_dispatch`. Сборка Jekyll (`jekyll-build-pages@v1` → `./_site`), затем `upload-pages-artifact@v3` и `deploy-pages@v4`. Environment `github-pages`.],
)

#shot(
  "6. Запуски Actions: ошибки и успех",
  `curl.exe …/actions/runs?per_page=10`,
  "shots/pr51/t51-06-runs.png",
  caption: [Два запуска с ветки `main` завершились ошибкой: (1) источник Pages ещё не был GitHub Actions; (2) ветка `main` не допущена правилами environment `github-pages`. Исправление — деплой с default-ветки `master`. Успешный run: https://github.com/Undeadguy0/Undeadguy0.github.io/actions/runs/43478406119],
)

#shot(
  "7. Шаги успешного run 43478406119",
  `curl.exe …/actions/runs/43478406119/jobs`,
  "shots/pr51/t51-07-jobs.png",
  caption: [Job `deploy`: все шаги `success`, включая Build with Jekyll и Deploy to GitHub Pages.],
)

#block(breakable: false)[
  #shot(
    "8. Проверка сайта",
    `curl.exe -I https://undeadguy0.github.io/ ; curl.exe -I …/hello.html`,
    "shots/pr51/t51-08-headers.png",
    caption: [Оба URL отвечают 200. Главная: «Главная | Бунто Михаил — Full-stack разработчик». `hello.html` — «GitHub Deployment Workflow». Сайт: https://undeadguy0.github.io/],
  )

  = Итог
  Репозиторий `Undeadguy0.github.io` публикуется GitHub Actions с ветки `master`.
  Главная визитка и `/hello.html` доступны по HTTPS (200).

  Сайт: #text(hyphenate: false)[https://undeadguy0.github.io/]

  Успешный pipeline:\
  #text(font: ("DejaVu Sans Mono", "Liberation Mono"), size: 8.5pt, hyphenate: false)[https://github.com/Undeadguy0/Undeadguy0.github.io/actions/runs/43478406119]
]
