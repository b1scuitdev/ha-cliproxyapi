"""Resolve the latest stable upstream image; update only declarative release pins."""
import hashlib
import json
import pathlib
import re
import urllib.request

root = pathlib.Path(__file__).resolve().parents[1]
def get(url, headers=None):
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers or {}), timeout=60) as response:
        return response.read()
release = json.loads(get('https://api.github.com/repos/router-for-me/CLIProxyAPI/releases/latest'))
assert not release['prerelease'] and not release['draft']
tag = release['tag_name']
assert re.fullmatch(r'v\d+\.\d+\.\d+', tag)
file = root / 'cliproxyapi/Dockerfile'
text = file.read_text()
if re.search(r'^FROM .*:' + re.escape(tag) + '@', text, re.M):
    raise SystemExit(0)
token = json.loads(get('https://auth.docker.io/token?service=registry.docker.io&scope=repository:eceasy/cli-proxy-api:pull'))['token']
index = get('https://registry-1.docker.io/v2/eceasy/cli-proxy-api/manifests/' + tag, {'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.list.v2+json'})
platforms = {(m['platform']['os'], m['platform']['architecture']) for m in json.loads(index)['manifests']}
assert {('linux', 'amd64'), ('linux', 'arm64')} <= platforms
pin = 'eceasy/cli-proxy-api:' + tag + '@sha256:' + hashlib.sha256(index).hexdigest()
file.write_text(re.sub(r'^FROM .*$', 'FROM ' + pin, text, count=1, flags=re.M))
manifest = root / 'cliproxyapi/config.yaml'
version = tag[1:] + '-1'
manifest.write_text(re.sub(r'^version: .*$', 'version: "' + version + '"', manifest.read_text(), flags=re.M))
changelog = root / 'cliproxyapi/CHANGELOG.md'
changelog.write_text('# ' + version + '\n\nUpdate official CLIProxyAPI to ' + tag + '. Review upstream release notes before merging.\n\n' + changelog.read_text())
print(version)
