FROM python:3.10-buster

ARG USER_NAME="user"
ARG USER_HOME="/${USER_NAME}"
ARG APP_HOME="${USER_HOME}/src"

RUN apt-get update

### Create service user ###
RUN groupadd -g 10001 ${USER_NAME} && useradd -g 10001 -u 10001 -s "/usr/sbin/nologin" -md ${USER_HOME} ${USER_NAME}

### Add application source code ###
COPY docker-entrypoint.sh /usr/local/bin/
COPY --chown=10001:10001 src/* ${APP_HOME}/

RUN pip install -r ${APP_HOME}/requirements.txt
ENV PYTHONPATH="${APP_HOME}"

USER ${USER_NAME}
WORKDIR ${APP_HOME}
ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["export"]
