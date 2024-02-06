# Rey Bot
This is a small project that I have been working on.
It's a personal/general purpose Discord bot with some of the commands I've implemented in the BWAE Services bot.

Currently it's implemented only Planetside 2 related commands, however, I plan to add a lot more stuff in the future.

### Commands

- `/server_panel` Return the current status of a server of your choice. Default: Emerald
- `/census_health` Return the current status of the Census API
- `/send_timestamp` Send a timestamp for an event given a time, date and event name
- `/get_ow_matches` Get the Outfit Wars matches for the current round! (Only working for Current Outfit Wars)
- `/get_ow_rankings` Get the Outfit Wars rankings for the server of your liking! (Only working for Current Outfit Wars)

Work In Progress!

## How to Run
I would prefer if you don't run an instance of my bot. Just call the join command with an invite URL to have it on your server. However, if you want to run it yourself, you can do so by following these steps:

I've included multiple ways to run the bot, so use whichever you prefer.
Note: Python 3.9 >= is required for the bot to run!
### Locally
1. Install dependencies using `pip install -r requirements.txt`
2. Modify the `config.cfg` file by filling the required config variables or add them as environment variables.
(Note: The genshin vars are currently for testing purposes)
3. Run the bot using `python bot.py` on windows or `python3 bot.py` on unix systems.

Note: A PostgreSQL database is being used for personal storage. I use a SupaBase instance, if you want to use it, you can get it [here](https://supabase.com/).
If you don't want to use a database, simply set the `host` variable under the [Database] section to empty in the config file.

### Docker
I included a docker installation since I'm using it to run it on my local server. If you want to use it, follow the steps below:
1. Install docker
2. Build the docker image: `docker build . -f bot.Dockerfile -t rey/rey_bot:latest`
3. Tag it: `docker tag rey/rey_bot localhost:5000/rey_bot`
4. Push it to your local registry: `docker push localhost:5000/rey_bot`
5. Run `docker-compose up -d`

## Contact
If you have any questions or inquiries, feel free to contact me on Discord:
**El Rey Zero#1501**