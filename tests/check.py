"""Static distribution checks; no secrets or provider accounts required."""
import pathlib
import re
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
c = yaml.safe_load((ROOT / 'cliproxyapi/config.yaml').read_text())
assert set(c['arch']) == {'aarch64', 'amd64'}
assert c['image'] == 'ghcr.io/b1scuitdev/ha-cliproxyapi'
assert c['ports'] == {'8317/tcp': 8317}
assert not any(c.get(k) for k in ('host_network', 'privileged', 'full_access', 'docker_api', 'hassio_api', 'homeassistant_api', 'ingress', 'devices'))
assert c.get('privileged', []) == []
assert c['schema'] == dict.fromkeys(c['options'], 'password?')
d = (ROOT / 'cliproxyapi/Dockerfile').read_text()
assert re.search(r'^FROM eceasy/cli-proxy-api:v\d+\.\d+\.\d+@sha256:[a-f0-9]{64}$', d, re.M)
assert c['version'].split('-')[0] in d
for name in ('io.hass.type', 'io.hass.version', 'io.hass.arch'):
    assert name in d
print('Distribution metadata checks passed')
