# Download base image python 3.11
FROM python:3.11

# LABEL about the custom image
LABEL maintainer="ElReyZero"
LABEL version="1.0"
LABEL description="This is a custom Docker Image for the ReyBot."

RUN mkdir "/home/ReyBot"
COPY bot.py /home/ReyBot/bot.py
COPY requirements.txt /home/ReyBot/requirements.txt
ADD discord_tools /home/ReyBot/discord_tools
ADD database /home/ReyBot/database
ADD utils /home/ReyBot/utils
ADD command_groups /home/ReyBot/command_groups
COPY utils/data/timezones.xlsx /home/ReyBot/utils/timezones.xlsx

RUN pip3 install -r /home/ReyBot/requirements.txt

ENTRYPOINT python3.11 /home/ReyBot/bot.py