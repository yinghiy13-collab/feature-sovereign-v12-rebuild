FROM python:3.12-slim
ARG OPA_VERSION=1.22.0
RUN apt-get update && apt-get install -y --no-install-recommends curl git ca-certificates && curl -fsSL -o /usr/local/bin/opa "https://openpolicyagent.org/downloads/v${OPA_VERSION}/opa_linux_amd64_static" && chmod +x /usr/local/bin/opa && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
