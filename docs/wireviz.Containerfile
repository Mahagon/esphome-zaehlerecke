# WireViz mit Graphviz, zum Erzeugen von verdrahtung.svg (siehe README)
FROM docker.io/library/python:3.12-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends graphviz \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir wireviz==0.4.1
WORKDIR /data
ENTRYPOINT ["wireviz"]
