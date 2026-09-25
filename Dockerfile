# Private Ceres Atlas qualification image.
# The image intentionally contains application code and the verified identity
# manifest only. WORLD, CIVSTATE, and MEDIA are external read-only mounts.
FROM python:3.13.7-slim-bookworm@sha256:adafcc17694d715c905b4c7bebd96907a1fd5cf183395f0ebc4d3428bd22d92d

LABEL org.opencontainers.image.title="LOOM 2226 Private Ceres Atlas" \
      org.opencontainers.image.description="Offline, read-only Ceres Atlas runtime; databases are external mounts" \
      org.opencontainers.image.source="https://github.com/loom-2226/loom-2226"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CERES_WORLD_DB=/data/world.sqlite3 \
    CERES_CIVSTATE_DB=/data/civstate.sqlite3 \
    CERES_MEDIA_DB=/data/media.sqlite3

WORKDIR /app
COPY tools/serve_ceres_atlas.py /app/tools/serve_ceres_atlas.py
COPY docs/ceres/manifest.json /app/docs/ceres/manifest.json
COPY web/ceres-atlas/index.html web/ceres-atlas/style.css web/ceres-atlas/app.mjs web/ceres-atlas/model.mjs /app/web/ceres-atlas/
COPY web/ceres-atlas/assets/loom-wordmark-white.svg /app/web/ceres-atlas/assets/loom-wordmark-white.svg

EXPOSE 8768
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8768/healthz', timeout=3)"

USER 65532:65532
ENTRYPOINT ["python", "-B", "tools/serve_ceres_atlas.py"]
CMD ["--host", "0.0.0.0", "--port", "8768", "--verify-startup"]
