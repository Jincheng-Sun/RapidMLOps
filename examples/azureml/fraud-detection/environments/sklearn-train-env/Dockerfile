FROM ${IMAGE_ARTIFACTORY_URL}/openmpi4.1.0-ubuntu20.04:latest

ENV PIP_INDEX_URL=${PIP_INDEX_URL}

RUN apt-get update && apt-get install -y \
    python3-pip \
    build-essential \
    libz-dev \
    libpng-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/bin/python3 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD ["python"]
