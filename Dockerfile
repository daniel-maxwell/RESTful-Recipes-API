# Use python 3.9 as base image with alpine 3.13 as base OS
FROM python:3.9-alpine3.13

# Set maintainer
LABEL maintainer="Daniel White"

# Print output from python directly to terminal
ENV PYTHONBUFFERED 1

# Copy requirements.txt in to the Docker Image
COPY ./requirements.txt /tmp/requirements.txt

# Copy dev requirements in to the Docker Image
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

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
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

# Add the virtual environment to the path environment variable
ENV PATH="/py/bin:$PATH"

# Switch to the django-user user
USER django-user