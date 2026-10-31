#!/bin/bash
set -euo pipefail
REPORT_DIR="${1:?Usage: check_policy.sh REPORT_DIRECTORY}"
SEVERITY_THRESHOLD="${SEVERITY_THRESHOLD:-HIGH,CRITICAL}"
python3 - "$REPORT_DIR" "$SEVERITY_THRESHOLD" <<'PY'
import json,pathlib,sys,csv
root=pathlib.Path(sys.argv[1]); blocked={x.strip().upper() for x in sys.argv[2].split(',') if x.strip()}
status=root/'scan-status.tsv'; inventory=root/'inventory.json'
if not status.is_file() or not inventory.is_file():
    print('POLICY ERROR: missing scan inventory or status',file=sys.stderr);sys.exit(2)
items=json.loads(inventory.read_text())
if not items:
    print('POLICY ERROR: empty inventory',file=sys.stderr);sys.exit(2)
rows=list(csv.reader(status.open(),delimiter='\t'))
if len(rows)!=len(items) or any(len(row)!=3 or row[2]!='OK' for row in rows):
    print('POLICY ERROR: incomplete scans',file=sys.stderr);sys.exit(2)
violations=0;summary=[]
for image,report,state in rows:
    try:
        p=pathlib.Path(report)
        if not p.is_file() or p.parent.resolve()!=root.resolve(): raise ValueError('Missing or invalid report path')
        data=json.loads(p.read_text())
        if not isinstance(data,dict) or not isinstance(data.get('Results'),list): raise ValueError('Invalid Trivy report')
        counts={}
        for result in data['Results']:
            for v in result.get('Vulnerabilities') or []:
                severity=str(v.get('Severity','UNKNOWN')).upper()
                counts[severity]=counts.get(severity,0)+1
        blocked_count=sum(counts.get(s,0) for s in blocked)
        violations+=blocked_count
        summary.append({'image_id':image,'report':report,'severity_counts':counts,'blocked_findings':blocked_count})
        print(f'{image}: {counts} | blocked={blocked_count}')
    except (OSError,ValueError,TypeError,json.JSONDecodeError) as exc:
        print(f'POLICY ERROR: {image}: {exc}',file=sys.stderr);sys.exit(2)
(root/'summary.json').write_text(json.dumps({'images':summary,'blocked_severities':sorted(blocked),'total_blocked_findings':violations},indent=2))
print(f'Images checked: {len(rows)}; blocked findings: {violations}')
if violations: print('POLICY FAILED');sys.exit(1)
print('POLICY PASSED')
PY
