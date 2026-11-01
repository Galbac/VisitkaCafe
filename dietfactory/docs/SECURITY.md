# Безопасность и развёртывание

## Локальный запуск

Используйте Docker Compose с поддержкой `!override` (2.24.4+):

```sh
docker compose -f docker-compose.yml -f compose.override.yaml up -d --build web db nginx
# Adminer при необходимости:
docker compose -f docker-compose.yml -f compose.override.yaml up -d adminer
```

Сайт со статикой: http://localhost/. Порты приложения, БД и Adminer доступны только с локальной машины. Ограничения POST работают через nginx; порт 8000 предназначен для локальной диагностики.

## Production

Используйте только основной Compose-файл, без локального override. Задайте `DEBUG=False`, явные `ALLOWED_HOSTS`, HTTPS-адреса в `CSRF_TRUSTED_ORIGINS`, уникальные пароли и `SECRET_KEY` от `python -c 'import secrets; print(secrets.token_urlsafe(64))'`. Никогда не публикуйте `.env`. Без достаточно сильного ключа production не стартует. Cookie защищены HTTPS, включены HTTPS redirect и HSTS без preload и без распространения на поддомены.

В основном Compose порт Gunicorn не публикуется: nginx — единственная публичная точка входа. Он перезаписывает forwarded-заголовки. Не публикуйте порт 8000 вручную и не подключайте к внутренней сети недоверенные контейнеры. База и Adminer привязаны к loopback; Adminer запускается только явно или с профилем `tools`.

Существующие каталоги данных нужно один раз передать пользователю приложения (UID/GID 1000). Перед изменением прав сделайте резервную копию:

```sh
docker compose -f docker-compose.yml --profile maintenance --profile tools build --pull
docker compose -f docker-compose.yml run --rm --no-deps --user root --cap-add CHOWN --entrypoint sh web -c 'chown -R 1000:1000 /app/media /app/staticfiles'
docker compose -f docker-compose.yml run --rm web python manage.py migrate --noinput
docker compose -f docker-compose.yml run --rm web python manage.py collectstatic --noinput
docker compose -f docker-compose.yml --profile maintenance up -d
docker compose -f docker-compose.yml exec -T web python manage.py check --deploy
docker compose -f docker-compose.yml exec -T web python manage.py audit_uploads
```

Рабочие сертификаты должны уже существовать в `/etc/letsencrypt/live/bezvreda05.ru/`; Certbot запускается по host systemd timer; настройка и dry-run описаны в DEPLOYMENT.md. Первичную выдачу выполняют на сервере, где DNS указывает на него и доступен порт 80. Не применяйте локальный HTTP override на публичном сервере.

`check --deploy` может предупреждать о выключенных HSTS preload и includeSubDomains: они намеренно не включены без проверки всех поддоменов и готовности к долгосрочной HTTPS-политике.

## Защита запросов и файлов

Nginx ограничивает POST к `/order/`, `/contact/`, `/reviews/` общим лимитом 5 запросов/минуту на IP, burst 5, и возвращает 429 при превышении. Вход в админку имеет отдельный аналогичный лимит. GET не расходуют лимит. IP берётся из соединения, а не из пользовательского X-Forwarded-For. За CDN потребуется отдельная конфигурация доверенных адресов real_ip; иначе лимит общий для адреса CDN. Это ограничение спама, а не полная защита от распределённой атаки.

Валидация форм, CSRF, лимиты длины и тела запроса работают в Django. Изображения проверяются по содержимому и ограничены 10 МБ/16 Мп; допустимы JPEG, PNG и WebP. SVG до 256 КБ проверяются XML-парсером без DTD/entities и белым списком тегов/атрибутов; скрипты, обработчики событий, CSS и внешние ссылки запрещены. Сертификаты принимаются как PDF или проверенные изображения. Проверка PDF заголовка не является антивирусом: дополнительно nginx отдаёт все media с CSP sandbox и nosniff, запрещает неизвестные расширения. Старые загрузки проверяются `audit_uploads` без их изменения.

Уведомления Telegram отправляются как ограниченный по длине обычный текст. Полные обращения сохраняются в БД. Токен, текст ответа Telegram и тела обращений не пишутся в журнал ошибок.

## Проверки

```sh
docker compose -f docker-compose.yml -f compose.override.yaml exec -T web python manage.py test --noinput
# Тот же набор на PostgreSQL, создаётся и удаляется отдельная test_ база:
docker compose -f docker-compose.yml -f compose.override.yaml exec -T -e TEST_DATABASE_ENGINE=postgres web python manage.py test --noinput
```

Отчёты `security/dependencies-before.json`, `security/dependencies-after.json` содержат результаты pip-audit для всех закреплённых зависимостей без игнорирования advisory. Повторять аудит нужно после обновлений и регулярно: отсутствие известных CVE сегодня не гарантирует отсутствие неизвестных уязвимостей. Совместимость установленных зависимостей проверяется `pip check` при сборке. После проверки pip и ensurepip удаляются из runtime, поскольку их встроенные библиотеки имеют отдельные CVE. Приложение использует Alpine и готовые колёса Python; компилятор и заголовки ядра в образ не устанавливаются. Все сервисы собираются через Dockerfile в docker/, чтобы получать актуальные системные патчи. PostgreSQL использует su-exec вместо gosu с устаревшим Go runtime. Certbot не содержит pip/uv. Проверка всех пяти образов: `bash scripts/audit-images.sh`.

## Эксплуатация

Резервируйте PostgreSQL через `pg_dump`, каталог `media` и отдельно секреты `.env`; храните копии с ограниченными правами вне публичных каталогов и проверяйте восстановление на отдельной базе. Не включайте резервные копии в Git/Docker. Ключи и токены, оказавшиеся в опубликованных старых образах или репозиториях, нужно отозвать у провайдера и заменить; удаление из нового образа не отзывает прежний секрет. Новые образы исключают `.env`, окружения, БД и журналы из build context.

Изменения в этом проекте проверяются локально. Применение их к рабочему серверу, его firewall, актуальность сертификатов, резервных копий и фактических секретов требуют проверки непосредственно в окружении сервера.
