# Using CLIProxyAPI

## First run

Install the app from the Home Assistant app store. Generate two independent keys
with `openssl rand -hex 32`, running it once per key. Enter them in
`initial_api_key` and `initial_management_key`, save, and start the app. Each key
must be at least 32 characters long and different from the other.

Open `http://HOME_ASSISTANT_IP:8317/management.html` and sign in with the management
key. Clear both initial key fields in Home Assistant after successful setup and
keep the keys in a password manager.

The API key authenticates model requests; the management key administers the
server. The HA fields are used only when `/data/config.yaml` does not exist.
Changing them later does not rotate keys or replace the config. Use upstream
management for subsequent changes. If you lose the management key, recover it
by editing the native config offline.

The initializer writes a minimal native config in JSON syntax, which is valid
YAML. CLIProxyAPI can hash the management secret and save the file using its own
YAML serializer. HA options and older backups may retain bootstrap secrets until
you clear or remove them.

## Configuration and OAuth

The original management panel owns configuration after setup. The native file is
`/data/config.yaml`; credentials are stored in `/data/auths`.

For Codex, start OAuth login in the panel, open the authorization URL on your
computer, and sign in. Submit the full returned callback URL through the panel's
callback submission feature. If your browser cannot open the localhost callback,
copy the URL from its address bar and submit it in the panel. Treat callback URLs
as secrets. Additional callback port mappings are not needed for this flow.
Repeat the process to connect multiple accounts.

Use upstream settings for account selection. For example, `routing.strategy`
can be set to `fill-first`, `routing.session-affinity` enables sticky sessions,
and `routing.retry` controls retries. The app starts with upstream defaults.
Consult the [configuration example for v8.0.67](https://github.com/router-for-me/CLIProxyAPI/blob/v8.0.67/config.example.yaml)
for field names and behavior, especially when following older guides.

## T3 Code

Configure your T3 model provider with the OpenAI-compatible base URL
`http://HOST:8317/v1` and the inference API key. For Codex CLI-based providers,
use Codex's standard custom model provider configuration with the Responses API.
Choose a model listed by `/v1/models`. The exact provider settings depend on
your installed T3 and provider versions.

For Usage Hub, open **Settings → Providers → Usage providers → Add hub**. Select
the environment that will connect, enter `http://HOST:8317`, and supply the
management key. This connection reports usage; configure inference separately.

T3 uses the upstream `/v0/management/auth-files`, `/v0/management/api-call`, and
`/v0/management/reset-quota` endpoints. Its management key grants administrative
permissions, including access to account credentials and configuration.
See the [T3 usage guide](https://github.com/pingdotgg/t3code/blob/main/docs/user/usage.md).
Live T3 and Codex account behavior require verification with your own setup.

## Network and security

Port 8317 is mapped to the HA host and accepts connections over its configured
interfaces, including the LAN. It is not restricted to Tailscale. Tailscale clients
need a route to the chosen host address; the app does not configure that route.
Keep public port forwarding and Funnel disabled for this service.

Remote management is enabled on first setup and requires its own key. The
management HTML page is publicly readable, while administrative data and actions
require authentication. Plain HTTP leaves LAN traffic unencrypted. Tailscale
protects traffic over its network path; upstream TLS is available if you also
want HTTPS on the LAN.

The app runs with standard container isolation and requests no host networking,
privileged access, Docker socket, host directory mounts, or HA API permissions.
Private data directories use mode 0700 and the startup process uses umask 077.
CLIProxyAPI controls permissions on files it writes. HA administrators and backup
holders can access secrets, so protect your backups.

The management panel's download and automatic update behavior follows upstream.
Its assets are updated independently of the pinned server image.

## Startup and watchdog

The app starts in the `application` stage, after Home Assistant Core. Enable
**Watchdog** in the Home Assistant app settings to use the Supervisor TCP check
on port 8317. It checks whether the listener accepts connections; it does not
validate provider availability, OAuth sessions, or successful model requests.
The check uses the app's internal address and container port, even if you change
the host port mapping. Keep the upstream listener on port 8317 for this check.

See the official [manifest reference](https://contributors.home-assistant.io/apps/reference/configuration/)
and [startup order](https://contributors.home-assistant.io/apps/how-apps-work/#starting).

## Updates and backups

New releases are reviewed before publication. Home Assistant detects the app
manifest version and offers an update. Leave automatic installation disabled,
back up the app, and approve updates manually. Image publication can take a few
minutes after a manifest change; retry after CI finishes if installation is
briefly unavailable.

Home Assistant app backups include `/data`:

| Path | Contents |
|---|---|
| `config.yaml` | Native upstream configuration |
| `auths/` | OAuth credentials and upstream credential state |
| `logs/` | File logs, when enabled |
| `plugins/` | Upstream plugins, when used |

These files survive restarts, container recreation, and app updates. Uninstalling
can delete app data, so take a backup first. Restore the app backup to recover its
configuration and credentials. For a portable export, use the original management
panel's configuration download and auth-file export; a full backup also retains
ancillary upstream state.

Before an update, keep a backup of both data and the installed version. To roll
back, restore that backup using Home Assistant's restore flow. A newer upstream
release may change its stored data, so avoid pairing an older server with files
already changed by a newer release.

## Moving to ordinary Docker

Securely copy the app's `/data` contents from a restored HA backup to a private
Linux directory. The native configuration and OAuth JSON need no conversion.

Mount that directory at `/data` in the official CLIProxyAPI Docker image, publish
`8317:8317`, and run `./CLIProxyAPI -config /data/config.yaml`. Mount the exported
`logs/` and `plugins/` directories at `/CLIProxyAPI/logs` and `/CLIProxyAPI/plugins`
if you use them, following upstream Compose conventions. Alternatively, adjust
the native path settings to match your ordinary Compose mounts.

Stop the HA instance before starting the new one. Credential files and the
upstream database should not be shared by two running instances. Retain restrictive
permissions and test access before removing the old installation.
