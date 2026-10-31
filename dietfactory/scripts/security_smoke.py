"""Read-only HTTP checks plus invalid POSTs: no requests can create a lead/order."""
import json
import urllib.error
import urllib.request

BASE = 'http://localhost'
results = {}


def request(path, *, body=None, headers=None):
    try:
        with urllib.request.urlopen(urllib.request.Request(
            BASE + path, data=body, headers=headers or {}), timeout=10) as response:
            return response.status, response.headers
    except urllib.error.HTTPError as error:
        return error.code, error.headers


for path in ['/', '/products/', '/certifications/', '/reviews/', '/privacy/',
             '/terms/', '/health/', '/static/assets/css/main.css', '/static/assets/img/logo.svg']:
    status, headers = request(path)
    assert status == 200, (path, status)
    results[path] = status
status, headers = request('/')
assert headers.get('X-Content-Type-Options') == 'nosniff'
assert headers.get('X-Frame-Options') == 'DENY'
assert headers.get('Referrer-Policy') == 'strict-origin-when-cross-origin'
# This body is invalid JSON and has no CSRF token; it cannot save a record or send Telegram.
statuses = [request('/contact/', body=b'{', headers={
    'Content-Type': 'application/json', 'X-Forwarded-For': f'198.51.100.{i+1}',
})[0] for i in range(12)]
assert 429 in statuses, statuses
assert all(code in {400, 403, 429} for code in statuses), statuses
assert request('/reviews/')[0] == 200
results['post_rate_limit_with_forged_forwarded_ips'] = statuses
# Separate login zone still accepts initial requests after the public zone is exhausted.
login_statuses = [request('/admin/login/', body=b'', headers={
    'Content-Type': 'application/x-www-form-urlencoded',
})[0] for _ in range(12)]
assert login_statuses[0] == 403, login_statuses
assert 429 in login_statuses, login_statuses
results['admin_login_rate_limit'] = login_statuses
results['security_headers'] = 'ok'
print(json.dumps(results, indent=2))
