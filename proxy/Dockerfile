# Set the base image to Ubuntu (unprivileged)
FROM nginxinc/nginx-unprivileged:1-alpine

# Set maintainer (me)
LABEL maintainer="Daniel White"

# Copy the config template in to the Docker Image
COPY ./default.conf.tpl /etc/nginx/default.conf.tpl

# Copy the uwsgi_params file in to the Docker Image
COPY ./uwsgi_params /etc/nginx/uwsgi_params

# Copy the run.sh script in to the Docker Image
COPY ./run.sh /run.sh

# Listen on port 8000
ENV LISTEN_PORT=8000

# Set the app host to app
ENV APP_HOST=app

# Set the app port to 8000
ENV APP_PORT=9000

# Switch to the root user for setup
USER root

# Commands to set up the image
RUN touch /etc/nginx/conf.d/default.conf && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    chmod 755 /run.sh
    chmod 777 ../app/db.sqlite3
    chown nginx:nginx ../app/db.sqlite3


# Switch to the (unprivileged) nginx user
USER nginx

# Run the run.sh script
CMD ["/run.sh"]