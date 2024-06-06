#!/bin/sh
# Replace environment variables in nginx template and start nginx
envsubst < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
exec nginx -g 'daemon off;'
