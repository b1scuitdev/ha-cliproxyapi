FROM eceasy/cli-proxy-api:v8.0.79@sha256:ce02dd2ba9186024762d8b6525c068c5a5fab78435b8d82d9c03f7ce74feeb5b
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
