FROM eceasy/cli-proxy-api:v8.0.67@sha256:2e098c0b3c79571f0c3150c8f27725ab2645b6a463cf6c4f862e4e86343466a1
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
