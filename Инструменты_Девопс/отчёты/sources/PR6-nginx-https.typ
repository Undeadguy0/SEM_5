#import "common.typ": *

#titlepage(
  work-type: "Практическая работа",
  number: 6,
  discipline: discipline,
  topic: "Веб-сервер и базовый деплой. Nginx, HTTP, TLS",
  group: group,
  student: student,
  teacher-position: teacher-position,
  teacher: teacher,
  year: year,
)

#show: gost.with(profile: "mirea")
#pagebreak()

= Цель отчёта
Подтверждение настроек Nginx + HTTPS для `devops.local`, прав на сайт и ключ,
результата `audit.sh` и снимка VirtualBox `04-nginx-https-T6`.

= Проверки

#shot(
  "1. Конфигурация Nginx и sites-enabled",
  `sudo nginx -t && ls -la /etc/nginx/sites-enabled/`,
  "shots/pr6/t6-01-nginx-t.png",
)

#shot(
  "2. HTTP → HTTPS редирект",
  `curl.exe -I --resolve devops.local:80:127.0.0.1 http://devops.local/`,
  "shots/pr6/t6-02-curl-http.png",
  caption: [Ожидается 301 на `https://devops.local/`. Запрос с хоста Windows через NAT `--resolve`.],
)

#shot(
  "3. HTTPS с доверенным сертификатом и SAN",
  `curl.exe --cacert ~/devops.crt -I --resolve devops.local:443:127.0.0.1 https://devops.local/`,
  "shots/pr6/t6-03-https-san.png",
)

#shot(
  "4. Права на закрытый ключ",
  `sudo ls -l /etc/ssl/private/devops.key`,
  "shots/pr6/t6-04-key.png",
  caption: [Режим `600`, владелец root.],
)

#shot(
  "5. Содержимое сайта и отсутствие world-writable",
  `ls -la /var/www/devops-site/; find … -perm -o+w`,
  "shots/pr6/t6-05-www.png",
  caption: [Пустой `find` — OK.],
)

#shot(
  "6. Деплой (таблица 10) — безопасная фиксация",
  `deploy.sh (dry-run / note)`,
  "shots/pr6/t6-06-deploy.png",
  caption: [Полные 5 сценариев (в т.ч. остановка nginx) не повторялись, чтобы не ломать прод-сайт. Деплой уже подтверждён снимком `04-nginx-https-T6` и `audit.sh`.],
)

#shot(
  "7. audit.sh",
  `(cd ~/devops-course-2026 && scripts/audit.sh); echo $?`,
  "shots/pr6/t6-07-audit.png",
  caption: [Ожидается `AUDIT_OK`, код 0. Блок \[4\] — веб-сервер.],
)

#shot(
  "8. Снимки VirtualBox",
  `VBoxManage snapshot devops-vm list`,
  "shots/pr6/t6-08-vbox.png",
  caption: [Выделен снимок `04-nginx-https-T6`.],
)

= Итог
Nginx обслуживает `devops.local` по HTTPS, HTTP редиректит на HTTPS, ключ `600`,
сайт без world-writable, `audit.sh` успешен, снимок T6 на месте.
