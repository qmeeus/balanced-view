ARG ELK_VERSION=7.4.0

# https://github.com/elastic/kibana-docker
FROM docker.elastic.co/beats/filebeat:${ELK_VERSION}

# Add your filebeat plugins setup here
RUN ./filebeat modules enable nginx
RUN ./filebeat setup -e

COPY ./config/filebeat.yml /usr/share/filebeat/filebeat.yml
USER root
RUN chown root:filebeat /usr/share/filebeat/filebeat.yml
USER filebeat
