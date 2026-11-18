FROM eceasy/cli-proxy-api:v8.0.77@sha256:2acf44fbadf9933a04e971048b4c2ddd184ce6e3ea08fc2dc25354f3a365f5ab
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
