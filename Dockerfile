FROM python:3.11-slim

WORKDIR /walk3r

COPY app/ app/
COPY pyproject.toml .
COPY README.md .

RUN pip install .

ENTRYPOINT ["python3", "-m", "app.cli"]
