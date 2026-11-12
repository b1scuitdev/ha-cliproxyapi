#!/bin/sh
set -eu
umask 077
mkdir -p /data/auths /data/logs /data/plugins
chmod 700 /data/auths /data/logs /data/plugins
if [ ! -e /data/config.yaml ]; then
    tmp=$(mktemp /data/.config.XXXXXX)
    trap 'rm -f "$tmp"' EXIT HUP INT TERM
    if ! jq -e '
      .initial_api_key as $api | .initial_management_key as $management |
      if (($api | type) == "string" and ($management | type) == "string") then
        if (($api | length) >= 32 and ($management | length) >= 32 and $api != $management)
        then {server: {host: "", port: 8317},
              management: {"allow-remote": true, "secret-key": $management},
              access: {"api-keys": [$api]}, oauth: {"auth-dir": "/data/auths"}}
        else error("invalid keys") end
      else error("missing keys") end
    ' /data/options.json > "$tmp" 2>/dev/null; then
        echo 'First run requires two distinct random bootstrap keys of at least 32 characters.' >&2
        exit 1
    fi
    # A hard link creates the config without replacing a concurrently created file.
    ln "$tmp" /data/config.yaml
    rm -f "$tmp"
    trap - EXIT HUP INT TERM
fi
exec /CLIProxyAPI/CLIProxyAPI -config /data/config.yaml
