#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
report_dir="$PWD/docs/security"
mkdir -p "$report_dir"
audit_tmp_dir="$(mktemp -d)"
trap 'rm -rf "$audit_tmp_dir"' EXIT
scanner_image="${TRIVY_IMAGE:-aquasec/trivy@sha256:790fd66d1697395d8693d1acaa1ea702406a20f109b6fc7bac8db623eca6c06c}"
for service in web postgres nginx adminer certbot; do
    docker image save "dietfactory-$service" -o "$audit_tmp_dir/image.tar"
    docker run --rm \
        -v "$audit_tmp_dir/image.tar:/scan/image.tar:ro" \
        -v /tmp/dietfactory-trivy-cache:/root/.cache/trivy \
        -v "$report_dir:/reports" \
        "$scanner_image" image --input /scan/image.tar --scanners vuln \
        --no-progress --format json --output "/reports/$service-after.json"
done
python3 - <<'PY'
import json
from collections import Counter
from pathlib import Path
failed = False
for name in ['web', 'postgres', 'nginx', 'adminer', 'certbot']:
    data = json.loads(Path(f'docs/security/{name}-after.json').read_text())
    vulnerabilities = [v for r in data.get('Results', []) for v in r.get('Vulnerabilities', [])]
    print(name, dict(Counter(v['Severity'] for v in vulnerabilities)))
    failed |= any(v['Severity'] in {'HIGH', 'CRITICAL'} for v in vulnerabilities)
raise SystemExit(1 if failed else 0)
PY
