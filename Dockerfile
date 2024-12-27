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

FROM gcr.io/distroless/cc-debian12:nonroot
COPY --from=build-env /app /app
COPY --from=build-env /opt/exiftool /opt/exiftool
COPY --from=build-env /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

ENV LD_LIBRARY_PATH=/usr/local/lib:/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}
ENV PYTHONPATH=/usr/local/lib/python3.12/site-packages
ENV PATH="/usr/local/bin:${PATH}"

COPY --from=build-env /usr/local/bin/python3.12 /usr/local/bin/python3
# Copy Python library files including shared libraries
COPY --from=build-env /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=build-env /usr/local/lib/libpython3.12.so* /usr/local/lib/
# Copy system libraries for x86_64
COPY --from=build-env /lib/x86_64-linux-gnu/lib* /lib/x86_64-linux-gnu/

ENV PATH="/opt/exiftool:${PATH}"
ENV EXIFTOOL_PATH="/opt/exiftool/"

# Verify that ExifTool binary exists
RUN [ -f /opt/exiftool/exiftool ] && echo "ExifTool binary exists" || echo "ExifTool binary missing"

WORKDIR /app
CMD ["/usr/local/bin/python3", "main.py"]