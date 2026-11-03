#import "common.typ": *

#titlepage(
  work-type: "Практическая работа",
  number: 7,
  discipline: discipline,
  topic: "Контейнеризация. Docker и Docker Compose",
  group: group,
  student: student,
  teacher-position: teacher-position,
  teacher: teacher,
  year: year,
)

#show: gost.with(profile: "mirea")
#pagebreak()

= Цель отчёта
Подтверждение Docker Compose стека `~/app` (app + db), публикации только на
`127.0.0.1:5000`, проксирования через Nginx `/app/`, режима `.env` и снимка
`05-docker-compose-T7`.

= Проверки

#shot(
  "1. Процесс в контейнере не root",
  `docker compose exec app id`,
  "shots/pr7/t7-01-id.png",
  caption: [uid=999(app) — не root.],
)

#shot(
  "2. Состояние compose",
  `docker compose ps`,
  "shots/pr7/t7-02-ps.png",
)

#shot(
  "3. Слушающие порты",
  `sudo ss -tlnp`,
  "shots/pr7/t7-03-ss.png",
  caption: [`127.0.0.1:5000` есть; `5432` не опубликован на хост.],
)

#shot(
  "4. `.env` не в git, режим 600",
  `git ls-files | grep .env; ls -l ~/app/.env`,
  "shots/pr7/t7-04-env.png",
)

#shot(
  "5. Прокси /app/ и корень сайта",
  `curl --cacert ~/devops.crt https://devops.local/app/ …`,
  "shots/pr7/t7-05-curl.png",
  caption: [Приложение отвечает через Nginx по HTTPS; корень сайта — 200.],
)

#shot(
  "6. audit.sh",
  `scripts/audit.sh`,
  "shots/pr7/t7-06-audit.png",
  caption: [Блок \[5\] контейнеризация — все OK.],
)

#shot(
  "7. Снимки VirtualBox",
  `VBoxManage snapshot devops-vm list`,
  "shots/pr7/t7-07-vbox.png",
  caption: [Снимок `05-docker-compose-T7`.],
)

= Итог
Compose-приложение работает без root, порты ограничены localhost, `.env` защищён,
Nginx проксирует `/app/`, audit и снимок T7 в порядке.
