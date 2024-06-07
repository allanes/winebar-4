#!/bin/sh
# Replace environment variables in nginx template and start nginx
envsubst '\${NGINX_INTERNAL_PORT} \${FRONTEND_CONTAINER_NAME} \${BACKEND_CONTAINER_NAME} \${FRONTEND_INTERNAL_PORT} \${BACKEND_INTERNAL_PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
exec nginx -g 'daemon off;'
