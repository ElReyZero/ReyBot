# Download base image ubuntu 20.04
FROM ubuntu:20.04

# LABEL about the custom image
LABEL maintainer="ElReyZero"
LABEL version="1.0"
LABEL description="This is custom Docker Image for the ReyBot."

# Disable Prompt During Packages Installation
ARG DEBIAN_FRONTEND=noninteractive

# Update Ubuntu Software repository
RUN apt update && apt dist-upgrade -y && apt install -y python python3 python3-pip git

RUN mkdir "/home/ReyBot"
COPY bot.py /home/ReyBot/bot.py
COPY config.py /home/ReyBot/config.py
COPY requirements.txt /home/ReyBot/requirements.txt
ADD discord_tools /home/ReyBot/discord_tools
COPY discord_tools/data/timezones.xlsx /home/ReyBot/discord_tools/timezones.xlsx

RUN pip3 install -r /home/ReyBot/requirements.txt

ENTRYPOINT python3 /home/ReyBot/bot.py