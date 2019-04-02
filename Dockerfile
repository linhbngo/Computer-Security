# This is a Dockerfile to build a Docker image for
# Operating Systems.

# We will start from a base Ubuntu 18.04
FROM i386/ubuntu:16.04

# Create non-root user, install dependencies, install Anaconda
RUN apt-get update --fix-missing && \
    apt-get install -y build-essential tmux git gdb wget && \
    sudo useradd -m -p WchOyJRR.1Qrc -s /bin/bash seed && \
    sudo usermod -a -G sudo seed && \
    apt-get install -y nano && \
    git clone https://github.com/linhbngo/Computer-Security.git /home/seed/Computer-Security && \
    chown -R seed:seed /home/student/Computer-Security

USER seed
ENV PATH "/bin:/usr/bin:$PATH"
WORKDIR "/home/seed"
CMD ["/bin/bash"]
