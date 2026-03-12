FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN SECRET_KEY='dummy-key-for-collectstatic' python manage.py collectstatic --noinput

# Expose port 8000
EXPOSE 8000

# Start server using gunicorn
CMD ["gunicorn", "bullet_journal.wsgi:application", "--bind", "0.0.0.0:8000"]
