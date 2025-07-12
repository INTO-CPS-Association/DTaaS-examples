FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt install -y sudo tzdata openjdk-17-jre python3 python3-pip && \
    ln -fs /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && \
    echo "Asia/Kolkata" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata && \
    pip3 install pandas matplotlib && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app