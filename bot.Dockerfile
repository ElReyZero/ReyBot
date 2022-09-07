# Download base image ubuntu 20.04
FROM ubuntu:22.04

# LABEL about the custom image
LABEL maintainer="ElReyZero"
LABEL version="1.0"
LABEL description="This is a custom Docker Image for the ReyBot."

# Disable Prompt During Packages Installation
ARG DEBIAN_FRONTEND=noninteractive

# Update Ubuntu Software repository
RUN apt update && apt dist-upgrade -y && apt install -y python3 python3-pip git
RUN python3 --version

RUN mkdir "/home/ReyBot"
COPY bot.py /home/ReyBot/bot.py
COPY config.py /home/ReyBot/config.py
COPY requirements.txt /home/ReyBot/requirements.txt
ADD discord_tools /home/ReyBot/discord_tools
ADD database /home/ReyBot/database
ADD utils /home/ReyBot/utils
ADD command_groups /home/ReyBot/command_groups
COPY utils/data/timezones.xlsx /home/ReyBot/utils/timezones.xlsx

RUN pip3 install -r /home/ReyBot/requirements.txt

ENTRYPOINT python3.10 /home/ReyBot/bot.py