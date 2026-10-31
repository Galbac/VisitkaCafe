FROM certbot/certbot:latest
# Runtime renewal uses the installed Certbot CLI, not package managers.
RUN apk upgrade --no-cache \
    && python -m pip check \
    && python -m pip uninstall --yes pip \
    && python -c "import shutil, sysconfig; shutil.rmtree(sysconfig.get_path('stdlib') + '/ensurepip', ignore_errors=True)" \
    && rm -f /usr/local/bin/uv /usr/local/bin/uvx \
    && certbot --version
