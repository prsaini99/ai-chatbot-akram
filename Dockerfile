FROM python:3.13-slim

WORKDIR /app

# Install dependencies for building Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install latest Rust (1.65+)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y \
    && . "$HOME/.cargo/env" \
    && rustc --version

# Ensure Rust is available in PATH for pip builds
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy requirements first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app
COPY . .

EXPOSE 5000
CMD ["python", "app.py"]
