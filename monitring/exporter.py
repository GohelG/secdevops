import json, os, pathlib, re, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
ROOT=pathlib.Path(os.getenv('REPORT_ROOT','/reports'))

def metrics():
    runs=sorted((p for p in ROOT.iterdir() if p.is_dir()),key=lambda p:p.stat().st_mtime,reverse=True) if ROOT.exists() else []
    lines=['# HELP secdevops_vulnerabilities Number of vulnerabilities in latest completed scan by image and severity','# TYPE secdevops_vulnerabilities gauge','# HELP secdevops_scan_success Whether image scan succeeded (1) or failed (0)','# TYPE secdevops_scan_success gauge','# HELP secdevops_last_scan_timestamp_seconds Timestamp of latest scan','# TYPE secdevops_last_scan_timestamp_seconds gauge']
    if not runs: return '\n'.join(lines)+'\n'
    run=runs[0]; inventory=json.loads((run/'inventory.json').read_text()) if (run/'inventory.json').exists() else []
    status={}
    if (run/'scan-status.tsv').exists():
        for row in (run/'scan-status.tsv').read_text().splitlines():
            parts=row.split('\t')
            if len(parts)==3: status[parts[0]]=parts[2]
    for n,item in enumerate(inventory,1):
        image=item.get('tags',[item['id']])[0] if item.get('tags') else item['id'][:24]
        image=image.replace('\\','\\\\').replace('"','\\"').replace('\n',' ')
        success=status.get(item['id'])=='OK'
        lines.append(f'secdevops_scan_success{{image="{image}"}} {int(success)}')
        path=run/f'image-{n:03d}.json'
        if not success or not path.exists():continue
        try:
            data=json.loads(path.read_text()); counts={s:0 for s in ('CRITICAL','HIGH','MEDIUM','LOW','UNKNOWN')}
            for result in data.get('Results',[]):
                for vuln in result.get('Vulnerabilities') or []:
                    sev=vuln.get('Severity','UNKNOWN').upper();counts[sev if sev in counts else 'UNKNOWN']+=1
            for severity,count in counts.items():lines.append(f'secdevops_vulnerabilities{{image="{image}",severity="{severity}"}} {count}')
        except (ValueError,OSError):pass
    lines.append(f'secdevops_last_scan_timestamp_seconds {int(run.stat().st_mtime)}')
    return '\n'.join(lines)+'\n'
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ('/metrics','/health'):
            self.send_error(404);return
        body=(metrics() if self.path=='/metrics' else 'ok\n').encode()
        self.send_response(200);self.send_header('Content-Type','text/plain; version=0.0.4; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
ThreadingHTTPServer(('0.0.0.0',9108),Handler).serve_forever()

