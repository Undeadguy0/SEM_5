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
  number: "5.2",
  discipline: discipline,
  topic: "Настройка удалённого сервера по SSH",
  group: group,
  student: student,
  teacher-position: teacher-position,
  teacher: teacher,
  year: year,
)

#show: gost.with(profile: "mirea")
#pagebreak()

= Цель отчёта
Подтверждение настройки удалённого Linux-сервера в VirtualBox для приёма
SSH-соединений: служба `ssh` запущена, SSH разрешён в UFW, порт 2222 хоста
проброшен на порт 22 гостя, в `sshd_config` задан `PermitRootLogin yes`,
выполнено подключение с Windows встроенным клиентом OpenSSH.

= Исходные условия
Вместо OVA-образа преподавателя (`sa` / `12345678`) использована уже
существующая ВМ `devops-vm` (Ubuntu 26.10, пользователь `devops`) из
предыдущих работ. Перед изменениями снят снимок `08-before-pr52`.
Вход выполняется по SSH-ключу (`PasswordAuthentication no` сохранён из
предыдущих работ), поэтому шаг «введите пароль» заменён аутентификацией по ключу.

= Проверки

#shot(
  "1. IP-адрес виртуальной машины",
  `hostname; whoami; ip -br addr`,
  "shots/pr52/t52-01-ipaddr.png",
  caption: [NAT-адаптер `enp0s3` — 10.0.2.15 (адрес для проброса портов), host-only `enp0s8` — 192.168.56.102.],
)

#shot(
  "2. Служба ssh",
  `sudo service ssh status`,
  "shots/pr52/t52-02-ssh-status.png",
  caption: [`ssh.service` — `active (running)`, автозапуск `enabled`. Перезапуск не потребовался.],
)

#shot(
  "3. UFW до изменений",
  `sudo ufw status verbose`,
  "shots/pr52/t52-03-ufw-before.png",
  caption: [Разрешены 80, 443 и 2222 (limit) из предыдущих работ. Правила для 22/tcp нет.],
)

#shot(
  "4. Резервные копии конфигурации",
  `sudo cp -a … .bak-pr52`,
  "shots/pr52/t52-04-backup.png",
  caption: [Созданы `/etc/ssh/sshd_config.bak-pr52` и `/etc/ssh/sshd_config.d/99-hardening.conf.bak-pr52`.],
)

#shot(
  "5. PermitRootLogin yes и проверка конфигурации",
  `sudo diff -u …; sudo sshd -t; sudo sshd -T`,
  "shots/pr52/t52-05-config.png",
  caption: [Основной `sshd_config` подключает `sshd_config.d/*.conf`, и значения из drop-in `99-hardening.conf` имеют приоритет, поэтому правка внесена туда: `PermitRootLogin yes`, добавлен `Port 22` (2222 сохранён). `sshd -t` — без ошибок, `sshd -T` подтверждает итоговые значения.],
)

#shot(
  "6. Перезапуск ssh и прослушиваемые порты",
  `sudo service ssh restart; sudo ss -tlnp | grep sshd`,
  "shots/pr52/t52-06-restart-ss.png",
  caption: [После перезапуска `sshd` слушает порты 22 и 2222 (IPv4 и IPv6).],
)

#shot(
  "7. Разрешение SSH в UFW",
  `sudo ufw allow ssh; sudo ufw status verbose`,
  "shots/pr52/t52-07-ufw-after.png",
  caption: [Добавлено правило `22/tcp ALLOW IN` (v4 и v6). Прежние правила 80/443/2222 не тронуты.],
)

#shot(
  "8. Проброс портов VirtualBox",
  `VBoxManage controlvm devops-vm natpf1 "ssh,tcp,127.0.0.1,2222,,22"`,
  "shots/pr52/t52-08-natpf.png",
  caption: [Правило `ssh` изменено на вид из методички: хост 127.0.0.1:2222 → гость :22. Правила http/https не изменялись.],
)

#shot(
  "9. OpenSSH в Windows",
  `Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH*'; ssh -V`,
  "shots/pr52/t52-09-win-openssh.png",
  caption: [Клиент OpenSSH уже установлен (`OpenSSH_for_Windows_9.5p2`). Сервер OpenSSH на Windows для подключения к ВМ не нужен и не устанавливался.],
)

#shot(
  "10. Подключение с Windows",
  `ssh -p 2222 devops@127.0.0.1 "hostname; whoami; uptime"`,
  "shots/pr52/t52-10-win-ssh.png",
  caption: [`SSH_CONNECTION` показывает, что соединение пришло через NAT (10.0.2.2) на порт 22 гостя.],
)

#shot(
  "11. Детали соединения",
  `ssh -v -p 2222 devops@127.0.0.1 exit`,
  "shots/pr52/t52-11-win-ssh-v.png",
  caption: [Сервер OpenSSH_10.5p1, ключ хоста ed25519, аутентификация `publickey`.],
)

#shot(
  "12. Вход без ключа",
  `ssh -p 2222 -o PubkeyAuthentication=no devops@127.0.0.1`,
  "shots/pr52/t52-12-nopass.png",
  caption: [Вход по паролю отключён: без ключа — `Permission denied (publickey)`.],
)

#shot(
  "13. Интерактивная сессия и выход",
  `ssh -p 2222 devops@127.0.0.1 → exit`,
  "shots/pr52/t52-14-interactive.png",
  caption: [Доступен терминал сервера, сессия завершена командой `exit`.],
)

#block(breakable: false)[
  #shot(
    "14. Сервисы предыдущих работ",
    `systemctl is-active nginx docker ssh; docker ps; curl https://devops.local/`,
    "shots/pr52/t52-13-services.png",
    caption: [nginx, docker и контейнеры KR2/PR7 работают, HTTPS отвечает 200.],
  )

  = Итог
  На сервере `devops-vm` служба SSH запущена и включена в автозапуск, SSH разрешён
  в UFW, порт 2222 хоста проброшен на порт 22 ВМ, в конфигурации задан
  `PermitRootLogin yes`. С Windows выполнено подключение `ssh -p 2222
  devops@127.0.0.1` встроенным клиентом OpenSSH. Состояние сохранено снимком
  `09-ssh-T52`.
]