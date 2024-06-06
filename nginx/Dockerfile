# nginx/Dockerfile
FROM nginx:stable

COPY ./nginx.conf.template /etc/nginx/nginx.conf.template
COPY ./entrypoint.sh /etc/nginx/entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /etc/nginx/entrypoint.sh
# RUN cat ls -al /etc/nginx

ENTRYPOINT ["/etc/nginx/entrypoint.sh"]
