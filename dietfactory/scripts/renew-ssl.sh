#!/bin/sh
# Run by the host timer. No Docker socket is exposed to the Certbot container.
set -eu
project_dir="${DIETFACTORY_PROJECT_DIR:-/root/dietfactory}"
exec 9>/run/lock/dietfactory-certbot.lock
flock -n 9 || exit 0
cd "$project_dir"
compose() {
    if [ -n "${DIETFACTORY_COMPOSE_OVERRIDE:-}" ]; then
        docker compose -f docker-compose.yml -f "$DIETFACTORY_COMPOSE_OVERRIDE" "$@"
    else
        docker compose -f docker-compose.yml "$@"
    fi
}
compose run --rm --no-deps certbot renew \
    --webroot -w /var/www/certbot --non-interactive --no-random-sleep-on-renew "$@"
compose exec -T nginx nginx -t
compose exec -T nginx nginx -s reload
