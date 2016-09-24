FROM continuumio/miniconda3:latest
MAINTAINER Samuel Taylor "docker@samueltaylor.org"

RUN conda install -y Flask requests beautifulsoup4

RUN conda install -y gunicorn
RUN apt-get install -y supervisor

ADD src/ /app

RUN /bin/bash -c 'cd /app/util/; python3 build_db.py'

ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 5000

CMD ["/usr/bin/supervisord"]
