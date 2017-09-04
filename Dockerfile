FROM python:3.5-alpine
ADD hazauth/ /hazauth/
WORKDIR /hazauth
RUN pip3.5 install requests docker redis && apk -q update && apk -q add docker
VOLUME /var/run/docker.sock:ro
ENTRYPOINT ["python","hazauth.py"]