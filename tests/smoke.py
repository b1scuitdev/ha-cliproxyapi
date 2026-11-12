"""Exercise the final image, real upstream server, and a synthetic SSE provider."""
import http.server
import json
import os
import pathlib
import secrets
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
import urllib.error
import yaml

image = sys.argv[1]
api, management = secrets.token_hex(32), secrets.token_hex(32)

def docker(*args, **kw):
    return subprocess.check_output(['docker', *args], text=True, **kw).strip()

def request(path, key=None, data=None, method=None):
    headers = {'Authorization': 'Bearer ' + key} if key else {}
    if data is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(data).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(base + path, data=data, headers=headers, method=method), timeout=60) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()

class Provider(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        assert self.headers['Authorization'] == 'Bearer fixture-only'
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        assert body['stream'] is True
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.end_headers()
        self.wfile.write(b'data: {"id":"fixture","object":"chat.completion.chunk","model":"fixture","choices":[{"index":0,"delta":{"content":"stream-ok"},"finish_reason":null}]}\n\n')
        self.wfile.flush()
        time.sleep(.1)
        self.wfile.write(b'data: {"id":"fixture","object":"chat.completion.chunk","model":"fixture","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}\n\ndata: [DONE]\n\n')
    def log_message(self, *args):
        pass

provider = http.server.ThreadingHTTPServer(('0.0.0.0', 0), Provider)
threading.Thread(target=provider.serve_forever, daemon=True).start()
with tempfile.TemporaryDirectory() as directory:
    data = pathlib.Path(directory)
    options = data / 'options.json'
    options.write_text(json.dumps({'initial_api_key': api, 'initial_management_key': management}))
    container = None
    def start():
        global container, base
        container = docker('run', '-d', '--cap-drop=ALL', '--security-opt=no-new-privileges', '--add-host=host.docker.internal:host-gateway', '-p', '127.0.0.1::8317', '-v', f'{data}:/data', image)
        try:
            port = docker('port', container, '8317/tcp').split(':')[-1]
        except subprocess.CalledProcessError:
            logs = docker('logs', container, stderr=subprocess.STDOUT)
            raise AssertionError(logs.replace(api, '[REDACTED]').replace(management, '[REDACTED]')) from None
        base = 'http://127.0.0.1:' + port
        for _ in range(90):
            try:
                if request('/v1/models', api)[0] == 200:
                    return
            except (OSError, urllib.error.URLError):
                pass
            if docker('inspect', '-f', '{{.State.Running}}', container) == 'false':
                break
            time.sleep(1)
        raise AssertionError('Upstream failed to start (logs intentionally withheld)')
    def stop():
        global container
        if container:
            docker('rm', '-f', container)
            container = None
    try:
        # Bad bootstrap must fail without creating config or printing input secrets.
        for bad in ({}, {'initial_api_key': 'short', 'initial_management_key': management}, {'initial_api_key': api, 'initial_management_key': api}):
            options.write_text(json.dumps(bad))
            result = subprocess.run(['docker', 'run', '--rm', '-v', f'{data}:/data', image], capture_output=True, text=True, timeout=30)
            assert result.returncode != 0 and not (data / 'config.yaml').exists()
            assert api not in result.stdout + result.stderr and management not in result.stdout + result.stderr
        options.write_text(json.dumps({'initial_api_key': api, 'initial_management_key': management}))
        start()
        for key in (None, 'wrong'):
            assert request('/v1/models', key)[0] == 401
            assert request('/v0/management/auth-files', key)[0] in (401, 403)
        assert request('/v0/management/auth-files', api)[0] in (401, 403)
        for path in ('/v0/management/config', '/v0/management/auth-files'):
            assert request(path, management)[0] == 200, path
        assert request('/v0/management/api-call', management, {})[0] == 400
        status, page = request('/management.html')
        assert status == 200 and b'<html' in page.lower()
        cfg = data / 'config.yaml'
        assert cfg.stat().st_mode & 0o077 == 0
        assert (data / 'auths').stat().st_mode & 0o077 == 0
        stop()
        original = cfg.read_bytes()
        marker = data / 'auths' / 'persistence.marker'
        marker.write_bytes(b'portable-oauth-storage')
        # Existing config must work even with absent bootstrap options.
        options.write_text('{}')
        start()
        assert cfg.read_bytes() == original
        assert marker.read_bytes() == b'portable-oauth-storage'
        stop()
        config = yaml.safe_load(cfg.read_text())
        config['openai-compatibility'] = [{'name': 'fixture', 'base-url': f'http://host.docker.internal:{provider.server_port}/v1', 'api-key-entries': [{'api-key': 'fixture-only'}], 'models': [{'name': 'fixture', 'alias': 'fixture'}]}]
        cfg.write_text(yaml.safe_dump(config))
        start()
        status, stream = request('/v1/chat/completions', api, {'model': 'fixture', 'messages': [{'role': 'user', 'content': 'test'}], 'stream': True})
        assert status == 200 and b'stream-ok' in stream and b'[DONE]' in stream
        assert not json.loads(docker('inspect', container))[0]['HostConfig']['Privileged']
        print('Real upstream startup, authentication, management page, persistence, and synthetic SSE passed')
    finally:
        stop()
        provider.shutdown()
