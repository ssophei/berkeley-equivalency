FROM python:3.12-bookworm
WORKDIR /app

# Install uv tool
RUN pip install --upgrade pip \
    && pip install --no-cache-dir uv

# Copy project for dependency installation
COPY pyproject.toml uv.lock* ./

# Let uv auto-create and sync the venv
RUN uv sync --frozen

# Install Playwright binaries
RUN uv run playwright install --with-deps

COPY src/ src/
COPY tests/ tests/
COPY data/ data/

CMD ["uv", "run", "pytest", "-q", "tests"]