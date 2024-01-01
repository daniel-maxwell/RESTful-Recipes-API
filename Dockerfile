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

# Work in the /app directory
WORKDIR /app

# Expose port 8000
EXPOSE 8000

# Create a virtual environment, install pip and dependencies, remove temp files and create a user
ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base musl-dev zlib zlib-dev linux-headers && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol && \
    chmod -R +x /scripts

# Add the virtual environment to the path environment variable
ENV PATH="/scripts:/py/bin:$PATH"

# Switch to the django-user user
USER django-user

# Run the run.sh script
CMD ["run.sh"]