# This is a Dockerfile to build a Docker image for
# Computer-Security

# We will start from a base Ubuntu 18.04
FROM i386/debian:buster

# Create sudo user, install dependencies
RUN apt-get update --fix-missing
RUN apt-get install -y build-essential
RUN apt-get install -y tmux
RUN apt-get install -y git
RUN apt-get install -y gdb
RUN apt-get install -y wget
RUN apt-get install -y sudo
RUN apt-get install -y nano

RUN useradd -m -p WchOyJRR.1Qrc -s /bin/bash seed && \
    usermod -a -G sudo seed

RUN git clone https://github.com/linhbngo/Computer-Security.git /home/seed/Computer-Security && \
    chown -R seed:seed /home/seed/Computer-Security

USER seed
ENV PATH "/bin:/usr/bin:$PATH"
WORKDIR "/home/seed"
CMD ["/bin/sh"]
