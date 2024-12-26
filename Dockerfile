FROM python:3.12-slim AS build-env

RUN apt-get update && apt-get install -y \
    curl

COPY . /app
WORKDIR /app

RUN mkdir -p /opt/exiftool \
&& cd /opt/exiftool \
&& EXIFTOOL_VERSION=`curl -s https://exiftool.org/ver.txt` \
&& EXIFTOOL_ARCHIVE=Image-ExifTool-${EXIFTOOL_VERSION}.tar.gz \
&& curl -s -O https://exiftool.org/$EXIFTOOL_ARCHIVE \
&& tar xzf $EXIFTOOL_ARCHIVE --strip-components=1 \
&& rm -f $EXIFTOOL_ARCHIVE \
&& exiftool -ver

FROM gcr.io/distroless/python3:nonroot
COPY --from=build-env /app /app
COPY --from=build-env /opt/exiftool /opt/exiftool
WORKDIR /app
CMD ["main.py"]