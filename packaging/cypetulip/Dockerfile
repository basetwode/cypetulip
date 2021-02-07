FROM python:3.9 as builder
ENV HOME=/opt/cypetulip/
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
    build-essential \
    libpq-dev \
    gettext \
    " \
    && seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{} \
    && apt-get update && apt-get install -y --no-install-recommends $RUN_DEPS \
    && rm -rf /var/lib/apt/lists/*

# Copy in your requirements file
COPY requirements.txt requirements.txt

RUN pip wheel --no-deps --no-cache-dir --wheel-dir /opt/cypetulip/wheels -r requirements.txt
ADD https://github.com/sass/dart-sass/releases/download/1.32.2/dart-sass-1.32.2-linux-x64.tar.gz /tmp/dart-sass/
RUN tar -xf /tmp/dart-sass/dart-sass-1.32.2-linux-x64.tar.gz -C /opt/


FROM python:3.9-slim-buster
RUN adduser app && adduser app app
COPY ./packaging/cypetulip/local_settings.py /etc/cypetulip/
# Copy your application code to the container (make sure you create a .dockerignore file if any large files or directories should be excluded)
WORKDIR /opt/cypetulip/

COPY --from=builder /opt/cypetulip/wheels /wheels
COPY --from=builder requirements.txt .
COPY --from=builder /opt/dart-sass /opt/dart-sass

RUN set -ex \
    && BUILD_DEPS=" \
    build-essential \
    libpq-dev \
    libpcre3-dev \
    " \
    && apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS \
    && pip install --no-cache /wheels/* \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
                                      && rm -rf /var/lib/apt/lists/*

COPY . /opt/cypetulip/
RUN set -ex \
    && BUILD_DEPS=" \
    gettext \
    libjpeg-dev \
    libopenjp2-7 \
    libtiff5 \
    " \
    && apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS \
    && rm -rf /var/lib/apt/lists/*

COPY ./packaging/cypetulip/entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

RUN mkdir /var/cypetulip/
RUN mkdir /var/cypetulip/static
RUN mkdir /var/cypetulip/company
RUN mkdir /var/cypetulip/orders
RUN mkdir /var/cypetulip/public
RUN chown -R app:app /var/cypetulip
RUN chown -R app:app /opt/cypetulip

USER app
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]