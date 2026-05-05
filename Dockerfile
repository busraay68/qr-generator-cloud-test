# Çok aşamalı kurulum, çalışma imajını küçük tutar.
FROM python:3.11-slim AS builder

WORKDIR /app

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

COPY pyproject.toml README.md ./
COPY src ./src

# Bağımlılıklar derleme aşamasında kurulur.
RUN pip install --upgrade pip && pip install .


FROM python:3.11-slim AS runtime

WORKDIR /app

ENV PATH="/opt/venv/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

COPY --from=builder /opt/venv /opt/venv
COPY src ./src

EXPOSE 8000

# Uygulama tek süreç olarak Uvicorn ile başlatılır.
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
