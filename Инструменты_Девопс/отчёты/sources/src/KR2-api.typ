#import "common.typ": *

#setup()
#title-page(
  "Контрольная работа № 2",
  "Вариант 1 — api.devops.local (порт 8001 → 127.0.0.1) · DEV_8 / T-KR2",
)

= Цель отчёта
Проверки шагов 3.2 / 4.1 для KR2: HTTPS API `api.devops.local`, счётчик с фамилией
Kisliy, изоляция порта 8001, сохранность devops.local, UFW без изменений, снимки
`06-before-kr2` / `07-kr2-TKR2`, PR на GitHub.

= Проверки

#shot(
  "1. HTTP → HTTPS для api.devops.local",
  `curl.exe -I --resolve api.devops.local:80:127.0.0.1 http://api.devops.local/`,
  "/shots/kr2/t8-01-http.png",
)

#shot(
  "2. HTTPS без cacert — ошибка сертификата",
  `curl.exe -I --resolve api.devops.local:443:127.0.0.1 https://api.devops.local/`,
  "/shots/kr2/t8-02-nocacert.png",
  caption: [Ожидается ошибка доверия (SEC_E_UNTRUSTED_ROOT / self-signed).],
)

#shot(
  "3. Корень API с cacert — счётчик Kisliy",
  `curl.exe --cacert ~/kr2.crt --resolve api.devops.local:443:127.0.0.1 https://api.devops.local/`,
  "/shots/kr2/t8-03-root.png",
)

#shot(
  "4. /whoami",
  `curl.exe --cacert ~/kr2.crt … https://api.devops.local/whoami`,
  "/shots/kr2/t8-04-whoami.png",
)

#shot(
  "5. devops.local и /app/ по-прежнему работают",
  `curl.exe --cacert ~/devops.crt -I https://devops.local/ … /app/`,
  "/shots/kr2/t8-05-devops.png",
)

#shot(
  "6. Порт 8001 с хоста недоступен",
  `curl.exe -m 3 --resolve api.devops.local:8001:127.0.0.1 http://api.devops.local:8001/health`,
  "/shots/kr2/t8-06-8001.png",
  caption: [Должен завершиться ошибкой: порт опубликован только на 127.0.0.1 внутри ВМ, наружу через NAT не проброшен.],
)

#shot(
  "7. SAN сертификата api.devops.local",
  `openssl s_client / x509 -ext subjectAltName`,
  "/shots/kr2/t8-07-san.png",
)

#shot(
  "8. audit.sh, UFW diff, ключ и .env, отсутствие паролей в файлах",
  `audit.sh; ufw; ls key/.env; password check`,
  "/shots/kr2/t8-08-audit-ufw.png",
  caption: [UFW правила не менялись относительно `~/ufw-before-kr2.txt`. Секреты только в `.env` (mode 600).],
)

#shot(
  "9. docker compose ps (kr2)",
  `docker compose -f ~/kr2/docker-compose.yml ps`,
  "/shots/kr2/t8-09-compose.png",
)

#shot(
  "10. Снимки VirtualBox",
  `VBoxManage snapshot devops-vm list`,
  "/shots/kr2/t8-10-vbox.png",
  caption: [`06-before-kr2`, `07-kr2-TKR2` (current).],
)

#shot(
  "11. GitHub Pull Request",
  `https://github.com/Undeadguy0/devops-kr2/pull/1`,
  "/shots/kr2/t8-11-pr.png",
)

= Итог
Вариант 1 выполнен: `api.devops.local` отдаёт счётчик Kisliy по HTTPS, порт 8001
изолирован, devops.local не сломан, UFW без изменений, audit OK, снимки и PR на месте.
