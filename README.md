# Rey Bot
This is a small project that I have been working on. 
It's a general purpose Discord bot with some of the commands I've implemented in the BWAE Services bot.

Currently it's implemented only Planetside 2 related commands, however, I plan to add a lot more stuff in the future.

### Commands

- `/server_panel` Return the current status of a server of your choice. Default: Emerald
- `/census_health` Return the current status of the Census API
- `/send_timestamp` Send a timestamp for an event given a time, date and event name
- `/get_ow_matches` Get the Outfit Wars matches for the current round! (Only working for Current Outfit Wars)

Work In Progress!

## How to Run
I've included multiple ways to run the bot, so use whichever you prefer.
### Locally
1. Install dependencies using `pip install -r requirements.txt`
2. Modify the `config.cfg` file by filling the required config variables or add them as environment variables.
(Note: The genshin vars are currently for testing purposes)
3. Run the bot using `python bot.py` on windows or `python3 bot.py` on unix systems.

Note: A MongoDB database is being used for personal storage. I use a MongoDB Atlas instance, if you want to use it, you can get it [here](https://www.mongodb.com/en/atlas/database)

### Docker
I included a docker installation since I'm using it to run it on my local server. If you want to use it, follow the steps below:
1. Install docker
2. Build the docker image: `docker build . -f bot.Dockerfile -t rey/rey_bot:latest`
3. Tag it: `docker tag rey/rey_bot localhost:5000/rey_bot`
4. Push it to your local registry: `docker push localhost:5000/rey_bot`
5. Run `docker-compose up -d`