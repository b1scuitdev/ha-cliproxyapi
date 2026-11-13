FROM eceasy/cli-proxy-api:v8.0.69@sha256:e77c1eecc0e364c1885a4441cdd6487ef305852851f70da723548736065c2e9b
ARG BUILD_VERSION
ARG BUILD_ARCH
LABEL io.hass.type="app" io.hass.version="${BUILD_VERSION}" io.hass.arch="${BUILD_ARCH}" \
      org.opencontainers.image.source="https://github.com/b1scuitdev/ha-cliproxyapi"
RUN apt-get update && apt-get install -y --no-install-recommends jq \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /data/logs /CLIProxyAPI/logs \
    && ln -s /data/plugins /CLIProxyAPI/plugins
COPY --chmod=755 run.sh /run.sh
ENV TZ=UTC
ENTRYPOINT ["/run.sh"]
CMD []
