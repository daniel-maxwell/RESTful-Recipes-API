# Use python 3.9 as base image with alpine 3.13 as base OS
FROM python:3.9-alpine3.13

# Set maintainer
LABEL maintainer="Daniel White"

# Print output from python directly to terminal
ENV PYTHONNUNBUFFERED 1

# Copy requirements.txt in to the Docker Image
COPY ./requirements.txt /tmp/requirements.txt

# Copy dev requirements in to the Docker Image
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Copy scripts directory in to the Docker Image
COPY ./scripts /scripts

# Copy app directory in to the Docker Image
COPY ./app /app

# Change ownership and permissions of the SQLite database file
RUN chown django-user:django-user /app/db.sqlite3 && \
    chmod 660 /app/db.sqlite3

# Work in the /app directory
WORKDIR /app

# Expose port 8000
EXPOSE 8000

# Create a virtual environment, install pip and dependencies, remove temp files and create a user
ARG DEV=false
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        build-base musl-dev zlib zlib-dev linux-headers && \
    python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    apk del .tmp-build-deps && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

# Add the virtual environment to the path environment variable
ENV PATH="/scripts:/py/bin:$PATH"

# Change ownership of necessary directories to django-user
RUN mkdir -p /app/staticfiles && \
    chown -R django-user:django-user /app && \
    chmod -R +x /scripts

# Switch to the django-user user
USER django-user

# Run the run.sh script
CMD ["run.sh"]