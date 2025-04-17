# SUSsh/docker/terminal-sandbox/Dockerfile

# Use Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Install bash, coreutils, and any useful tools (optional: nano, less, etc.)
RUN apt update && apt install -y \
    bash \
    coreutils \
    && useradd -m discordbot

# Switch to non-root user for safety
USER discordbot

# Set working directory
WORKDIR /home/discordbot

# Launch a bash shell when container starts
CMD ["bash"]
