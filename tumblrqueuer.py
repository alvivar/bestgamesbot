""" Script that queues Tumblr posts from the Itch.io scrapper data. """

import json
import os
import re
import sys
import time

import itchioscrapper
import pytumblr

if __name__ == "__main__":

    DELTA = time.time()
    print("bestgamesintheplanet [Bot]\n")

    # Frozen / not frozen, cxfreeze compatibility
    DIR = os.path.normpath(
        os.path.dirname(
            sys.executable if getattr(sys, 'frozen', False) else __file__))
    os.chdir(DIR)  # The current dir is the script one

    # Files
    TOKENS_FILE = "tokens.json"
    DONE_FILE = "tumblr_done.json"

    # Tumblr tokens are mandatory
    try:
        TOKENS = json.load(open(TOKENS_FILE, 'r'))
    except (IOError, ValueError):
        TOKENS = {
            'consumer_key': "",
            'consumer_secret': "",
            'oauth_token': "",
            'oauth_secret': ""
        }
        with open(TOKENS_FILE, "w") as f:
            json.dump(TOKENS, f)

    if not TOKENS['consumer_key']:
        print(f"I need your Tumblr API tokens!\n"
              f"Write them in {TOKENS_FILE} and try again.")
        input("OK?")
        sys.exit(0)

    # Tumblr connection
    API = pytumblr.TumblrRestClient(
        TOKENS['consumer_key'],
        TOKENS['consumer_secret'],
        TOKENS['oauth_token'],
        TOKENS['oauth_secret'],
    )

    # Already queued games
    try:
        DONE = json.load(open(DONE_FILE, 'r'))
    except (IOError, ValueError):
        DONE = {}

    # Queue new games
    GAMES = itchioscrapper.get_games("https://itch.io/games")
    GAMES = {k: v for k, v in GAMES.items() if k not in DONE}

    # The game url is the 'k'ey
    for k, v in GAMES.items():

        win = "Windows " if v['windows'] else ""
        mac = "Mac " if v['mac'] else ""
        lin = "Linux " if v['linux'] else ""
        web = "Web " if v['web'] else ""
        android = "Android " if v['android'] else ""

        platforms = (win + mac + lin + web + android).strip()
        platforms_title = platforms.replace(" ", ", ")
        platforms_title = f"({platforms_title})" if platforms_title else ""

        tags = f"{v['author']} {v['title']} {platforms}"
        tags = re.split("[^0-9a-zA-Z]", tags)
        tags = [t.lower() for t in tags if t]
        giftag = ["gif"] if v['gif'] else []
        tags = ["videogame", "indiegame", "gaming", "itchio"] + giftag + tags

        title = f"# [{v['title']}]({k}) ([{v['author']}]({v['author_url']}))\n\n"
        description = f"## {v['description']}\n\n" if v['description'] else ""

        price_title = f"Buy it for {v['price']}" if v[
            'price'] else "Free to play"
        price = f"### [{price_title}]({k}) {platforms_title}"

        result = API.create_photo(
            "bestgamesintheplanet",
            state="queue",
            tags=tags,
            format="markdown",
            caption=f"{title}{description}{price}",
            source=f"{v['gif'] if v['gif'] else v['image']}")

        if result:
            print(f"New: {k}")
            DONE[k] = v
            with open(DONE_FILE, "w") as f:
                json.dump(DONE, f)

    # Info log
    COUNT = len(GAMES)
    print(
        f"{COUNT} game{'s' if COUNT != 1 else ''} found ({round(time.time()-DELTA)}s)"
    )
    input("OK?")
