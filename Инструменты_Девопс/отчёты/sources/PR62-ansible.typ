#import "common.typ": *

// Keep each check (heading + command + screenshot + caption) on one page.
#let shot(title, cmd, path, caption: none, w: 100%) = {
  block(breakable: false)[
    #heading(level: 2, title)
    #if cmd != none {
      block(width: 100%, inset: 6pt, fill: luma(245), stroke: 0.4pt + luma(200))[
        #text(font: ("DejaVu Sans Mono", "Liberation Mono"), size: 8.5pt)[#cmd]
      ]
    }
    #v(0.25cm)
    #image(path, width: w)
    #if caption != none {
      v(0.15cm)
      text(9pt, fill: luma(80))[#caption]
    }
    #v(0.4cm)
  ]
}

#titlepage(
  work-type: "Практическая работа",
  number: "6.2",
  discipline: discipline,
  topic: "Управление конфигурацией с помощью Ansible",
  group: group,
  student: student,
  teacher-position: teacher-position,
  teacher: teacher,
  year: year,
)

#show: gost.with(profile: "mirea")
#pagebreak()

= Цель отчёта
Подтверждение настройки сервера из работы 5.2 с помощью Ansible: playbook `setup.yml`
с ролями `base`, `nginx`, `app`, `ssh`, файл `inventory.ini`, теги ролей,
идемпотентность повторного запуска и запуск отдельных ролей по тегам.

= Исходные условия и схема
- Управляемый сервер — ВМ `devops-vm` (Ubuntu 26.10) из работы 5.2. Перед изменениями снят снимок `12-before-pr62`.
- Управляющий узел — WSL Ubuntu в Windows. ansible-core 2.22.0 установлен в venv пользователя (`~/ansible-venv`): в WSL нет pip и sudo без пароля.
- Подключение: порт NAT VirtualBox (127.0.0.1:2222 → гость :22) слушается на loopback Windows и из WSL недоступен. Поэтому в `inventory.ini` Ansible использует клиент Windows OpenSSH: `ansible_ssh_executable=…/ssh.exe`, алиас `devops` из `~/.ssh/config` Windows, вход по ключу, `ControlMaster=no`, `ansible_ssh_transfer_method=piped`. Права root — через `become` (sudo).
- Каталог проекта `/mnt/h/...` в WSL доступен всем на запись, и Ansible игнорирует `./ansible.cfg`. Обёртка `run.sh` задаёт `ANSIBLE_CONFIG` явно, inventory передаётся через `-i inventory.ini`.
- Чтобы не затронуть сервисы прошлых работ (`devops.local`, `/app/`, `api.devops.local`, статический сайт 6.1), роль `nginx` добавляет *отдельный* сайт `app.devops.local` и не меняет существующие. Роль `ssh` управляет drop-in `99-hardening.conf` с теми же настройками, что после работы 5.2 (проверка `sshd -t -f %s`, `backup: yes`). Полное `apt upgrade` в роли `base` есть, но выключено по умолчанию (`base_upgrade: false`), чтобы не перезапускать docker/nginx предыдущих работ. Выполняется обновление кэша apt.

= Проверки

#shot(
  "1. Версия Ansible и связь с сервером",
  `./run.sh ansible --version; ansible -i inventory.ini web -m ping`,
  "shots/pr62/t62-01-version-ping.png",
  caption: [Используется `ansible.cfg` проекта. `ping` → `pong`.],
)

#shot(
  "2. Структура проекта",
  `find . -type f | sort; tar tvzf roles/app/files/site.tar.gz`,
  "shots/pr62/t62-02-tree.png",
  caption: [Роли `base`, `nginx`, `app`, `ssh` (tasks/handlers/defaults/templates/files). Архив сайта `site.tar.gz` собирается из `site-src/`.],
)

#shot(
  "3. inventory.ini, setup.yml, переменные",
  `cat inventory.ini setup.yml group_vars/web.yml run.sh ansible.cfg`,
  "shots/pr62/t62-04a-inventory-setup.png",
  caption: [Группа `web` с сервером `devops-vm`. Роли выполняются последовательно, каждой назначен тег.],
)

#shot(
  "4. Роль base",
  `cat roles/base/tasks/main.yml roles/base/defaults/main.yml`,
  "shots/pr62/t62-04b-role-base.png",
  caption: [Кэш apt, утилиты (curl, git, htop, tree, unzip, rsync), fail2ban с jail `sshd` для портов 22/2222. Адреса хоста и NAT в `ignoreip`, чтобы не заблокировать себя.],
)

#shot(
  "5. Роль nginx",
  `cat roles/nginx/tasks/main.yml roles/nginx/handlers/main.yml`,
  "shots/pr62/t62-04c-role-nginx.png",
  caption: [Установка и запуск nginx, сайт `pr62-app` из шаблона. Handler сначала выполняет `nginx -t`, затем `reload`.],
)

#shot(
  "6. Роль app",
  `cat roles/app/tasks/main.yml roles/nginx/templates/pr62-app.conf.j2`,
  "shots/pr62/t62-04d-role-app.png",
  caption: [`unarchive` загружает архив `site.tar.gz` на сервер и распаковывает его в `/var/www/pr62-app`. Затем проверяется HTTP 200.],
)

#shot(
  "7. Роль ssh",
  `cat roles/ssh/tasks/main.yml roles/ssh/defaults/main.yml roles/ssh/handlers/main.yml`,
  "shots/pr62/t62-04e-role-ssh.png",
  caption: [Открытый ключ `devops_vm.pub` добавляется в `authorized_keys`. Конфигурация sshd проверяется `sshd -t` до замены файла.],
  w: 80%,
)

#shot(
  "8. Проверка синтаксиса и список тегов",
  `ansible-playbook -i inventory.ini setup.yml --syntax-check; … --list-tags`,
  "shots/pr62/t62-03-syntax-tags.png",
  caption: [Теги: `app`, `base`, `nginx`, `ssh`.],
)

#shot(
  "9. Первый запуск (часть 1): роль base",
  `ansible-playbook -i inventory.ini setup.yml --diff`,
  "shots/pr62/t62-05-run1-a.png",
  caption: [Установлены fail2ban, tree, unzip и зависимости, создан jail.],
)

#shot(
  "10. Первый запуск (часть 2): nginx и app — ошибка",
  none,
  "shots/pr62/t62-05-run1-b.png",
  caption: [Сайт и каталог созданы, архив распакован. Проверка через модуль `uri` упала: с заголовком `Host` он пытался резолвить `app.devops.local`. Кроме того, reload nginx не успел выполниться, так как handlers запускаются в конце play. Исправления: проверка через `curl` и `meta: flush_handlers` в конце роли nginx.],
  w: 85%,
)

#shot(
  "11. Первый запуск после исправления",
  `ansible-playbook -i inventory.ini setup.yml --diff`,
  "shots/pr62/t62-05-run1b.png",
  caption: [`nginx -t` и reload выполнены handler-ами, сайт развёрнут, страница отвечает 200. Роль ssh — `ok`: настройки из работы 5.2 совпадают с шаблоном. `failed=0`.],
  w: 90%,
)

#shot(
  "12. Повторный запуск — идемпотентность",
  `ansible-playbook -i inventory.ini setup.yml`,
  "shots/pr62/t62-06-run2.png",
  caption: [`changed=0`: система уже соответствует описанию, изменений нет.],
)

#shot(
  "13. Запуск только роли app",
  `ansible-playbook -i inventory.ini setup.yml --tags "app"`,
  "shots/pr62/t62-07-tag-app.png",
  caption: [Выполняются только задачи роли `app`.],
)

#shot(
  "14. Обновление сайта через тег app",
  `ansible-playbook -i inventory.ini setup.yml --tags "app"   # после правки index.html`,
  "shots/pr62/t62-07b-tag-app-change.png",
  caption: [После изменения страницы и пересборки архива изменена одна задача — распаковка архива (`changed=1`).],
)

#shot(
  "15. Запуск только роли ssh",
  `ansible-playbook -i inventory.ini setup.yml --tags "ssh"`,
  "shots/pr62/t62-08-tag-ssh.png",
  caption: [Ключ уже добавлен, конфигурация sshd совпадает — `changed=0`.],
)

#shot(
  "16. Список задач по тегам base,nginx",
  `ansible-playbook -i inventory.ini setup.yml --list-tasks --tags "base,nginx"`,
  "shots/pr62/t62-09-list-tasks.png",
)

#shot(
  "17. Результат роли base",
  `ansible web -m command -a "fail2ban-client status sshd"; ansible web -m shell -a "dpkg -l …"`,
  "shots/pr62/t62-10-base-check.png",
  caption: [fail2ban работает, jail `sshd` активен. Утилиты установлены.],
)

#shot(
  "18. Страница приложения",
  `curl.exe -H "Host: app.devops.local" http://127.0.0.1/`,
  "shots/pr62/t62-11-app-http.png",
  caption: [Страница из архива отдаётся nginx (200), CSS — `text/css`.],
)

#shot(
  "19. Сайт в браузере",
  `msedge --headless --host-resolver-rules="MAP app.devops.local 192.168.56.102" http://app.devops.local/`,
  "shots/pr62/t62-14-browser.png",
  w: 80%,
)

#shot(
  "20. Сервисы предыдущих работ",
  `curl.exe … devops.local / /app/ / api.devops.local / 192.168.56.102; sshd -T; docker ps`,
  "shots/pr62/t62-12-earlier-labs.png",
  caption: [HTTPS `devops.local`, `/app/`, `api.devops.local` — 200, статический сайт 6.1 — «Версия: 2». Настройки SSH из 5.2 сохранены, контейнеры работают.],
)

#block(breakable: false)[
  #shot(
    "21. Удаление временного правила sudo",
    `sudo visudo -c; sudo rm /etc/sudoers.d/90-devops-lab && sudo -k; sudo -n true`,
    "shots/pr62/t62-13-sudoers-removed.png",
    caption: [Временный NOPASSWD-доступ для работ 5.2–6.2 удалён. `sudo -n` снова требует пароль.],
  )

  = Итог
  Playbook `setup.yml` с ролями `base`, `nginx`, `app`, `ssh` и инвентарём
  `inventory.ini` настраивает сервер `devops-vm`. Повторный запуск идемпотентен
  (`changed=0`), отдельные роли запускаются по тегам (`--tags "app"`, `--tags "ssh"`).
  Сервисы предыдущих работ не затронуты. Состояние сохранено снимком `13-ansible-T62`.
]