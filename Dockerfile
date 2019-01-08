FROM
MAINTAINER Tobias Schoch <tobias.schoch@vtxmail.ch>

# Install dependencies
RUN apt-get update && apt-get install -y \
    git-core \
    build-essential \
    gcc \
    python \
    python-dev \
    python-pip \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Define working directory
WORKDIR /data
VOLUME /data

CMD ["/bin/bash"]