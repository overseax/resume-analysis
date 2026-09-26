FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md requirements.txt ./
COPY src ./src
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir . --no-deps

ENTRYPOINT ["resume-cli"]
