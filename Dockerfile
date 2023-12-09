FROM python:3.12

# COPY . /app
# WORKDIR /app

# install poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/etc/poetry python3 -
ENV PATH "/etc/poetry/venv/bin/:${PATH}"

# Copy poetry.lock* in case it doesn't exist in the repository
COPY poetry.lock* pyproject.toml /app/

# Set working directory
WORKDIR /app

# install python requirements
# RUN poetry install --no-root --only main --no-interaction
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

RUN apt-get update && apt-get install -y pngquant

# Copy application code
COPY . /app

RUN pwd
RUN ls -la

# run server
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5005", "--app-dir", "src"]




