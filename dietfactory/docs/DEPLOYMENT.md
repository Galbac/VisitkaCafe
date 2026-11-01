# Выкладка и SSL

Рабочий проект: `/root/dietfactory`, HTTPS: `bezvreda05.ru` и `www.bezvreda05.ru`.

Репозиторий: `https://github.com/Galbac/VisitkaCafe.git`, ветка `main`. На сервере Git-checkout находится в `/root/VisitkaCafe`; `/root/dietfactory` — совместимая ссылка на `/root/VisitkaCafe/dietfactory`. Sparse checkout включает только каталог приложения, без отслеживаемого в корне репозитория виртуального окружения.

Порядок обновления: сначала commit и push в `origin/main` локально, затем `git pull --ff-only origin main` на сервере. Перед обновлением сохраняются `.env`, media, дамп PostgreSQL и прежний образ приложения. `.env` и media игнорируются Git и сохраняются при pull. Локальный Compose override на production не используется.

```sh
git -C /root/VisitkaCafe pull --ff-only origin main
cd /root/dietfactory
docker compose -f docker-compose.yml --profile maintenance --profile tools build
docker compose -f docker-compose.yml run --rm --no-deps web python manage.py migrate --noinput
docker compose -f docker-compose.yml run --rm --no-deps web python manage.py collectstatic --noinput
docker compose -f docker-compose.yml up -d db web nginx adminer
```

При первоначальном переводе на Git прежний каталог сохраняется целиком вне checkout, а `.env` и media переносятся с сохранением прав. Образы и существующие именованные тома PostgreSQL/static/certbot сохраняются; имя Compose-проекта остаётся `dietfactory`.

После сборки всех образов: один раз выдать UID/GID 1000 права на media/static volume, выполнить migrate и collectstatic, затем обновить контейнеры. ManifestStaticFilesStorage создаёт хешированные имена CSS/JS, чтобы браузеры не сохраняли старую верстку после выкладки.

## Автообновление SSL

Certbot запускается одноразово из исправленного Docker-образа по host systemd timer. Режим webroot использует общий том `/var/www/certbot`; nginx обслуживает ACME challenge на HTTP без остановки сайта. Docker socket в контейнер не монтируется.

```sh
cd /root/dietfactory
docker compose -f docker-compose.yml --profile maintenance --profile tools build
# При смене authenticator сначала проверить и сохранить webroot-настройки:
docker compose -f docker-compose.yml run --rm --no-deps certbot reconfigure \
  --cert-name bezvreda05.ru --webroot -w /var/www/certbot --non-interactive
install -m 0755 scripts/renew-ssl.sh /usr/local/sbin/dietfactory-renew-ssl
install -m 0644 deploy/systemd/dietfactory-certbot-renew.* /etc/systemd/system/
systemctl daemon-reload
/usr/local/sbin/dietfactory-renew-ssl --dry-run
# После успешной проверки единственный планировщик:
systemctl disable --now certbot.timer
systemctl enable --now dietfactory-certbot-renew.timer
systemctl list-timers dietfactory-certbot-renew.timer
```

Скрипт `renew-ssl.sh` использует flock от параллельных запусков. При успешном renew выполняет `nginx -t` и reload, включая случай, когда продление ещё не требуется. При ошибке Certbot перезагрузка не выполняется, service имеет ошибочный статус в systemd/journal. Таймер срабатывает дважды в сутки с задержкой до часа, `Persistent=true` компенсирует пропущенный запуск после перезагрузки. Профиль `maintenance` не запускает постоянный конкурирующий Certbot-контейнер.

Dry-run использует staging Let's Encrypt и не заменяет действующий production-сертификат. Проверять:

```sh
systemctl status dietfactory-certbot-renew.timer
journalctl -u dietfactory-certbot-renew.service --since '7 days ago'
openssl x509 -in /etc/letsencrypt/live/bezvreda05.ru/fullchain.pem -noout -dates
curl -I https://bezvreda05.ru/
```

## Проверка 1 ноября 2026

Обновление выполнено на `177.177.212.26`. Исходники, `.env`, media, PostgreSQL и `/etc/letsencrypt` сохранены в `/root/dietfactory-backups/pre-20261101-ui-security` (каталог 0700, копии 0600); прежний образ приложения имеет тег `dietfactory-web:pre-20261101`.

- Новый интерфейс проверен локально и на публичном HTTPS в Chromium: ширины 320, 375, 390, 440, 768, 1024, 1440; нет переполнения и JS-ошибок. Проверены ссылки сертификатов/отзывов, меню, поиск и белый текст кнопки.
- Локально на временных записях дополнительно проверены просмотр сертификата, оригинал, Escape и товар/страница товара; записи удалены. Production-данные тестовыми записями не заполнялись.
- 31 Django-тест прошёл на сервере с изолированной SQLite; тот же набор прошёл локально на PostgreSQL. Внешние уведомления тестами не отправлялись.
- `certbot reconfigure` сохранил `authenticator=webroot`; production ACME остался `https://acme-v02.api.letsencrypt.org/directory`.
- Полный сценарий с `renew --dry-run` завершился `all simulated renewals succeeded`, затем nginx -t и reload. Серийный номер действующего сертификата не изменился, срок действия до **29 января 2027, 19:34:53 UTC**.
- Нормальный запуск `dietfactory-certbot-renew.service` без тестовых сетевых настроек завершился `Result=success`, `ExecMainStatus=0`. Таймер enabled/active; прежний `certbot.timer` disabled. Постоянный Certbot-контейнер удалён, конкурирующего цикла нет.
- На HTTPS включён HSTS `max-age=31536000`, приложение не публикует порт 8000, БД healthy.

### Сетевые особенности staging и www

Адрес staging Let’s Encrypt недоступен напрямую с сервера (таймаут), при этом production ACME доступен и отвечает 200. Для staging-проверки использовался временный loopback HTTP CONNECT туннель через SSH с сохранением сквозного TLS и проверкой имени staging. Через `DIETFACTORY_COMPOSE_OVERRIDE` только тестовому Certbot передавались host network и временный HTTPS_PROXY. После успешной проверки override и SSH-forward удалены, локальный процесс остановлен. В systemd unit и обычном Compose прокси не настроен; штатное продление протестировано отдельно после удаления маршрута. При повторном прямом dry-run этот сетевой таймаут возможен снова: требуется доступный маршрут именно к staging, а не отключение проверки TLS.

`www.bezvreda05.ru` в момент проверки указывает на **45.130.41.157**, а основной домен — на **177.177.212.26**. Текущий сертификат покрывает только `bezvreda05.ru`. Для поддержки www нужно изменить его DNS A-запись у DNS-провайдера и затем добавить www в сертификат. Доступа к управлению DNS в этой задаче не предоставлено, чужой сервер не изменялся.

Официальное поведение reconfigure/dry-run: [руководство Certbot](https://eff-certbot.readthedocs.io/en/latest/using.html#modifying-the-renewal-configuration-of-existing-certificates).
