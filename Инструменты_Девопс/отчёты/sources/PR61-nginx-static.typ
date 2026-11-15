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
  number: "6.1",
  discipline: discipline,
  topic: "Статический сервер сайта",
  group: group,
  student: student,
  teacher-position: teacher-position,
  teacher: teacher,
  year: year,
)

#show: gost.with(profile: "mirea")
#pagebreak()

= Цель отчёта
Подтверждение того, что на удалённом сервере из работы 5.2 nginx отдаёт
статический сайт (HTML, CSS, изображение), а изменения разворачиваются
с локальной машины через `rsync` сценарием `deploy.sh`.

= Исходные условия и выбранная схема
- Сервер — ВМ `devops-vm` из работы 5.2 (Ubuntu 26.10, nginx 1.30.4). Перед изменениями снят снимок `10-before-pr61`.
- На nginx уже работают `devops.local` (HTTPS, работа 6), `/app/` (работа 7) и `api.devops.local` (КР2). Чтобы их не затронуть, сайт вынесен в *отдельный* server block `static-site` (HTTP, порт 80) с `server_name static.devops.local 192.168.56.102`. Существующие файлы конфигурации не редактировались. Перед изменениями `/etc/nginx` сохранён в `/etc/nginx.bak-pr61.tar.gz`.
- Новые правила UFW и проброса портов не понадобились: 80/tcp уже открыт, NAT 127.0.0.1:80 → :80 уже есть. Сайт доступен по IP сервера `http://192.168.56.102/` (host-only) и по имени `static.devops.local`. Файл hosts в Windows не менялся: имя передаётся заголовком `Host` / `curl --resolve`.
- В Windows `rsync` нет, поэтому `deploy.sh` запускается в WSL (Ubuntu, rsync 3.4.1). Транспорт — Windows OpenSSH (`rsync -e ssh.exe`), так как порт NAT VirtualBox 2222 слушается на loopback Windows.
- Публичный домен (cloudpub.ru / freedns.afraid.org) в методичке необязателен и не настраивался: для него нужна регистрация в сторонних сервисах.

= Проверки

#shot(
  "1. Подключение к серверу по SSH",
  `ssh devops "hostname; whoami; nginx -v; systemctl is-active nginx"`,
  "shots/pr61/t61-01-ssh.png",
  caption: [Подключение через 127.0.0.1:2222 → гость :22 (из работы 5.2). nginx установлен и запущен.],
)

#shot(
  "2. Конфигурация nginx до изменений",
  `ls -l /etc/nginx/sites-enabled/; sudo nginx -T | grep -E "listen|server_name"`,
  "shots/pr61/t61-02-nginx-before.png",
  caption: [Включены сайты `devops-site` и `kr2`.],
)

#shot(
  "3. Резервная копия, каталог сайта, server block",
  `sudo tar czf /etc/nginx.bak-pr61.tar.gz …; sudo tee /etc/nginx/sites-available/static-site; sudo nginx -t`,
  "shots/pr61/t61-03-setup.png",
  caption: [Корень сайта `/var/www/static-site` принадлежит `devops`, поэтому rsync работает без sudo. Новый сайт включён симлинком, `nginx -t` — успешно.],
)

#shot(
  "4. rsync на клиенте и сервере",
  `Get-Command rsync; wsl rsync --version; ssh devops rsync --version`,
  "shots/pr61/t61-03b-rsync.png",
  caption: [В Windows rsync отсутствует, используется rsync из WSL Ubuntu. На сервере — rsync 3.5.0.],
)

#shot(
  "5. Локальный статический сайт",
  `_work\pr61-site: index.html, css/style.css, img/logo.png`,
  "shots/pr61/t61-04-site.png",
  caption: [Страница с HTML, CSS и изображением. Строка «Версия» используется для проверки обновления.],
)

#shot(
  "6. Сценарий deploy.sh",
  `cat deploy.sh`,
  "shots/pr61/t61-04b-deploy-sh.png",
  caption: [`rsync -av --delete` в `/var/www/static-site/`, затем `nginx -t` и `reload`, затем проверка HTTP-кода и версии страницы. Ненулевой код возврата при любой ошибке (`set -euo pipefail`).],
)

#shot(
  "7. Первый запуск deploy.sh",
  `bash deploy.sh`,
  "shots/pr61/t61-05-deploy-1.png",
  caption: [Каталог на сервере был пуст: переданы все файлы, сайт отвечает 200, «Версия: 1».],
)

#shot(
  "8. Повторный запуск без изменений",
  `bash deploy.sh`,
  "shots/pr61/t61-06-deploy-2.png",
  caption: [rsync не передал ни одного файла — содержимое уже совпадает.],
)

#shot(
  "9. Запуск после изменения страницы",
  `bash deploy.sh   # после правки «Версия: 1» → «Версия: 2»`,
  "shots/pr61/t61-07-deploy-3.png",
  caption: [Передан только изменённый `index.html`, сайт отдаёт «Версия: 2».],
)

#shot(
  "10. Проверка по HTTP с Windows",
  `curl.exe -H "Host: static.devops.local" http://127.0.0.1/; curl.exe --resolve …; curl.exe http://192.168.56.102/`,
  "shots/pr61/t61-08-http.png",
  caption: [HTML, CSS и PNG отдаются с правильными типами. Сайт доступен и по IP сервера.],
)

#shot(
  "11. Сайт в браузере",
  `msedge --headless --screenshot http://192.168.56.102/`,
  "shots/pr61/t61-11-browser.png",
  caption: [Страница с применённым CSS и изображением, загружена с nginx по IP сервера.],
)

#shot(
  "12. Файлы и журнал доступа на сервере",
  `ls -lR /var/www/static-site; sudo tail /var/log/nginx/static-site.access.log`,
  "shots/pr61/t61-10-server.png",
  caption: [Файлы на сервере совпадают с локальными. В журнале — запросы с хоста (192.168.56.1), включая загрузку CSS и изображения браузером.],
)

#block(breakable: false)[
  #shot(
    "13. Сервисы предыдущих работ",
    `curl.exe -sk --resolve … https://devops.local/ /app/ https://api.devops.local/`,
    "shots/pr61/t61-09-earlier-labs.png",
    caption: [`devops.local` (200), `/app/` (200), `api.devops.local` (200), редирект HTTP→HTTPS (301) работают как раньше. Контейнеры запущены. UFW не менялся.],
  )

  = Итог
  На сервере `devops-vm` nginx отдаёт статический сайт из `/var/www/static-site`
  через отдельный server block (`static.devops.local`, `http://192.168.56.102/`).
  Сайт разворачивается сценарием `deploy.sh` (rsync + `nginx -t` + reload + проверка HTTP).
  Повторные запуски передают только изменённые файлы. Сервисы предыдущих работ
  не затронуты. Состояние сохранено снимком `11-nginx-static-T61`.
]