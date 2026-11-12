# Contributing

This repository packages the official CLIProxyAPI image for Home Assistant OS.
Keep deployment changes small and use upstream configuration for server behavior.

## Container layout

`cliproxyapi/Dockerfile` extends `eceasy/cli-proxy-api`, pinned to a stable release
and its immutable multiarchitecture digest. It adds jq for first-run option
parsing, a startup script, HA labels, and persistent log/plugin links. The
upstream executable is unchanged.

`run.sh` initializes `/data/config.yaml` only when absent, then execs CLIProxyAPI.
Existing config bypasses bootstrap entirely. HA supplies persistent `/data`,
process reaping, and restart management. Only port 8317 is published; browser
OAuth uses upstream callback submission.

## Local checks

On Linux with Python and Docker:

```sh
python -m pip install PyYAML==6.0.3
python tests/check.py
sh -n cliproxyapi/run.sh

docker build \
  --build-arg BUILD_VERSION=8.0.67-1 \
  --build-arg BUILD_ARCH=amd64 \
  -t ha-cliproxyapi:test cliproxyapi
sudo "$(command -v python)" tests/smoke.py ha-cliproxyapi:test
```

Use the version in `cliproxyapi/config.yaml` and your native HA architecture
(`amd64` or `aarch64`). The smoke test needs root access to inspect the container's
private files on its temporary bind mount. Its provider fixture runs on the
Docker host and is reached through `host.docker.internal`.

CI runs the HA app linter and tests on native AMD64 and ARM64 runners. Tests cover
real upstream startup, bootstrap validation, API and management authentication,
management endpoints and page, file permissions, storage across container
recreation, unchanged existing config, and SSE through a synthetic provider.

Real OAuth login and refresh, quota checks, multi-account failover, T3 clients,
and HAOS installation and backup restoration need account or hardware testing.
Record those checks separately when performed.

## Upstream updates and releases

The scheduled update workflow checks GitHub's latest stable upstream release.
`tests/update.py` resolves the official image, requires both Linux architectures,
and records the index's SHA-256 digest in the Dockerfile. It updates the app
version and changelog, then the workflow proposes a PR.

GitHub requires the repository's combined “Allow GitHub Actions to create and
approve pull requests” setting for these PRs. The workflow creates PRs only; it
does not approve or merge them. Configure that setting explicitly if enabling
update automation.

PRs opened with the default Actions token do not trigger PR workflows. Manually
run **Build, test and publish** on the update branch, review upstream release
notes and test results, then merge. Startup and endpoint incompatibilities fail
smoke tests; provider behavior changes also need human review.

Pushes to `app` run both architecture suites before publishing the tested images
to GHCR. Published version tags are retained on reruns. Use a new wrapper revision
for a changed image, even when the upstream version stays the same. Ensure the
GHCR package is publicly pullable and set branch protection to require checks
for future PRs. App installation remains a separate manual action in HA.

The server image is pinned; upstream management-panel assets keep their own
update lifecycle. Retain upstream license notices when distributing its image.
