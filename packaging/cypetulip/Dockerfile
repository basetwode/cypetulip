FROM python:3.8.3


ENV HOME=/opt/cypetulip/

RUN adduser app && adduser app app
# Install packages needed to run your application (not build deps):
#   mime-support -- for mime types when serving static files
#   postgresql-client -- for running database commands
# We need to recreate the /usr/share/man/man{1..8} directories first because
# they were clobbered by a parent image.
RUN set -ex \
    && RUN_DEPS=" \
    libpcre3 \
    mime-support \
    postgresql-client \
    gettext \
    " \
    && seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{} \
    && apt-get update && apt-get install -y --no-install-recommends $RUN_DEPS \
    && rm -rf /var/lib/apt/lists/*

# Copy in your requirements file
COPY requirements.txt requirements.txt

# OR, if you're using a directory for your requirements, copy everything (comment out the above and uncomment this if so):
# ADD requirements /requirements

# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step.
# Correct the path to your production requirements file, if needed.
RUN set -ex \
    && BUILD_DEPS=" \
    build-essential \
    libpcre3-dev \
    libpq-dev \
    " \
    && apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS \
    && pip install --no-cache-dir -r /requirements.txt \
    \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
    && rm -rf /var/lib/apt/lists/*


COPY ./packaging/cypetulip/local_settings.py /etc/cypetulip/

# todo cron.d
# todo fix permissions on shared volumes so it can be run as app:app
# test deploy

# Copy your application code to the container (make sure you create a .dockerignore file if any large files or directories should be excluded)

WORKDIR /opt/cypetulip/
COPY . /opt/cypetulip/

ADD https://github.com/sass/dart-sass/releases/download/1.32.2/dart-sass-1.32.2-linux-x64.tar.gz /tmp/dart-sass/
RUN tar -xf /tmp/dart-sass/dart-sass-1.32.2-linux-x64.tar.gz -C /opt/
#RUN wget https://github.com/sass/dart-sass/releases/download/1.32.2/dart-sass-1.32.2-linux-x64.tar.gz && tar -xf dart-sass-1.32.2-linux-x64.tar.gz


COPY ./packaging/cypetulip/entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

RUN pip install -r /opt/cypetulip/requirements.txt
RUN mkdir /var/cypetulip
RUN chown -R app:app /opt/cypetulip
RUN chown -R app:app /var/cypetulip
USER app
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]