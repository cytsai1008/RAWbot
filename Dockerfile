FROM python:3.12-slim AS build-env

RUN apt-get update && apt-get install -y \
    curl

COPY . /app

RUN mkdir -p /opt/exiftool \
&& cd /opt/exiftool \
&& EXIFTOOL_VERSION=$(curl -s https://exiftool.org/ver.txt) \
&& EXIFTOOL_ARCHIVE=Image-ExifTool-${EXIFTOOL_VERSION}.tar.gz \
&& curl -s -O https://exiftool.org/$EXIFTOOL_ARCHIVE \
&& tar xzf $EXIFTOOL_ARCHIVE --strip-components=1 \
&& rm -f $EXIFTOOL_ARCHIVE \
&& chmod +x exiftool \
&& /opt/exiftool/exiftool -ver

WORKDIR /app

RUN pip install --upgrade pip wheel \
&& pip install --no-cache-dir -r requirements.txt

ENV PATH="/opt/exiftool:${PATH}"
ENV EXIFTOOL_PATH="/opt/exiftool/"

WORKDIR /app
CMD ["/usr/local/bin/python3", "main.py"]