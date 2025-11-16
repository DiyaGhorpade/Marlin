FROM nvidia/cuda:12.2.2-devel-ubuntu22.04

# Set DEBIAN_FRONTEND to noninteractive to prevent tzdata configuration dialog
ENV DEBIAN_FRONTEND=noninteractive

# Set UTF-8 locale to avoid encoding issues in Python / Jupyter
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

USER root

# Set the working directory
WORKDIR /app

# Mount volumes
VOLUME /data

# Install gnupg
RUN apt-get update && apt-get install -y \
    gnupg \
    cmake \
    build-essential \
    dkms \
    wget \
    apt-utils \
    pkg-config \
    libcairo2-dev \
    software-properties-common \
    python3-cairo-dev \
    netstat-nat \
    telnet \
    curl \
    iputils-ping \
    netcat-openbsd \
    python3-venv \
    python3-dev \
    postgresql-client \
    tesseract-ocr \
    poppler-utils \
    dos2unix && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download and install pip for Python 3 using get-pip.py script
RUN apt-get update && apt-get install -y curl python3-venv
RUN apt-get install -y python3-dev
RUN ln -s /usr/bin/python3 /usr/bin/python

# Add a line to activate the virtual environment in ~/.bashrc
RUN echo "source /myvenv/bin/activate" >> /root/.bashrc

# Copy requirements
COPY requirements.txt .
COPY .env .
COPY jupyter-settings/ /root/.jupyter/lab/user-settings/

# Ensure pip is compatible with the CUDA version
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3

# Create and activate a virtual environment
RUN python3 -m venv /myvenv && \
    . /myvenv/bin/activate && \
    pip install pycairo && \
    pip install -r requirements.txt

# documentation only
EXPOSE 8888

# Copy the start script and make it executable
COPY app/ /app/

# Copy scripts
COPY wait-for-kafka.sh /app/
COPY wait-for-postgres.sh /app/
COPY start.sh /app/


RUN dos2unix wait-for-kafka.sh && chmod +x wait-for-kafka.sh
RUN dos2unix wait-for-postgres.sh && chmod +x wait-for-postgres.sh
RUN dos2unix start.sh && chmod +x start.sh

# Start your application with CMD
CMD ["/app/start.sh"]