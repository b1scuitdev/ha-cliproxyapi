FROM eceasy/cli-proxy-api:v8.1.8@sha256:29717a242f16aa12256b36a2d86f5ac7bbfe2dd002f23ce66eeb27fddbc096c0
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
