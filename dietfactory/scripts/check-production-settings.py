"""Check production guards in disposable containers, without real secrets or a DB."""
import json
import subprocess

KEY = 'deployment-check-only-7q9P-X3aK-6cVe-8mBw-2rTs-5dFg-4hJn'


def run(key, hosts, expression):
    return subprocess.run([
        'docker', 'run', '--rm', '--env', 'DJANGO_SETTINGS_MODULE=dietfactory.settings', '--env', 'DEBUG=False', '--env', 'SECRET_KEY=' + key,
        '--env', 'ALLOWED_HOSTS=' + hosts, 'dietfactory-web', 'python', '-c', expression,
    ], capture_output=True, text=True, timeout=30)


result = run(KEY, 'example.com', '''
from django.conf import settings
import json
print(json.dumps({
    'debug_disabled': settings.DEBUG is False,
    'session_cookie_secure': settings.SESSION_COOKIE_SECURE,
    'csrf_cookie_secure': settings.CSRF_COOKIE_SECURE,
    'https_redirect': settings.SECURE_SSL_REDIRECT,
    'hsts': settings.SECURE_HSTS_SECONDS > 0,
    'forwarded_host_not_trusted': not settings.USE_X_FORWARDED_HOST,
}))
''')
assert result.returncode == 0, result.stderr
checks = json.loads(result.stdout)
assert all(checks.values()), checks
for label, key, hosts, message in [
    ('weak_key_rejected', 'short', 'example.com', 'strong SECRET_KEY'),
    ('wildcard_host_rejected', KEY, '*', 'explicit ALLOWED_HOSTS'),
]:
    result = run(key, hosts, 'from django.conf import settings; print(settings.DEBUG)')
    checks[label] = result.returncode != 0 and message in result.stderr
    assert checks[label], result.stderr
print(json.dumps(checks, indent=2))
