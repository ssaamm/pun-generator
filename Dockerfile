FROM continuumio/miniconda3:latest
MAINTAINER Samuel Taylor "docker@samueltaylor.org"

# Web requirements
RUN apt-get update && apt-get install -y supervisor nginx
RUN conda install -y gunicorn

# nginx
RUN rm /etc/nginx/sites-enabled/default
RUN ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled/nginx.conf
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY config/nginx.conf /etc/nginx/sites-available/
RUN mkdir /logs

# supervisord
ADD config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# App-specific stuff
RUN conda install -y Flask requests beautifulsoup4
ADD src/ /app
RUN /bin/bash -c 'mkdir -p /app/data; cd /app/util/; python3 build_db.py'

EXPOSE 80

CMD ["/usr/bin/supervisord"]
