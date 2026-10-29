# Public-safe demo image: code, prompts and the SYNTHETIC mini fixture pack only.
# The supplied assignment pack, replay recordings (which quote real answers), outputs,
# databases and .env are excluded (.dockerignore). Tokens come from the environment.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PACK_DIR=tests/fixtures/mini_pack MODEL_PROVIDER=stub DATABASE_PATH=/tmp/answerscope.db \
    REPLAY_DIR=/tmp/replay
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app app
COPY prompts prompts
COPY tests/fixtures/mini_pack tests/fixtures/mini_pack
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
CMD ["sh", "-c", "python -m app.cli init-db && exec uvicorn app.main:create_app --factory --host 0.0.0.0 --port ${PORT:-8000}"]
