FROM postgres:17-alpine
# su-exec performs the same UID/GID drop without shipping an outdated Go runtime.
RUN apk add --no-cache su-exec \
    && apk upgrade --no-cache \
    && sed -i 's/exec gosu /exec su-exec /g' /usr/local/bin/docker-entrypoint.sh \
    && rm -f /usr/local/bin/gosu
