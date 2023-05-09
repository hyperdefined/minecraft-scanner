# minecraft-scanner
A small project I made in an afternoon for fun. I'm not a python or node programmer, so have fun looking at the code. This project uses the Shodan API to find Minecraft servers and saves them locally. On request, it will update the saved servers with new information from Shodan. Afterwards, it attempts to join the server.

1. Create `.env` with these contents:
```
SHODAN_KEY=<key>
MINECRAFT=<Minecraft email>
```

2. Run `npm install` and `pip install pandas shodan dotenv`
3. Run `python3 shodan_query.py` to load new servers from Shodan. Afterwards, it will save them to the database and join random ones.
    * Run `python3 shodan_query.py update` to update existing servers first, then load new ones and join.
4. If you want to change what the bot does when it joins, edit the `join_server.js` file.
## Problems
* Some Forge servers hide mod information, so Shodan cannot detect if they are using Forge. You will find a lot of servers that do not work and complain about you not using Forge. Nothing I can really do.
* Program is very slow.