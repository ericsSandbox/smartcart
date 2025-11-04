FROM python:3.12-slim

# Install system dependencies required to build psycopg2, pg_isready, tesseract OCR, and Chrome
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    chromium \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser binaries
RUN playwright install chromium firefox webkit

# Copy entrypoint first and set permissions
COPY entrypoint.sh /code/
RUN chmod 755 /code/entrypoint.sh

# Copy the rest of the code
COPY . .

ENTRYPOINT ["/code/entrypoint.sh"]
