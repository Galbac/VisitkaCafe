FROM adminer:latest
USER root
RUN apk upgrade --no-cache
USER adminer
