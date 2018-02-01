""" Script that queues Tumblr posts from the Itch.io scrapper data.

    TODO
    - Use twitter user on tumblr publication if available?
"""

import json
import os
import re
import shutil
import sys
import time
from urllib.request import Request, urlopen

import pytumblr
import qbotqueuer
from itchioscrapper import get_games

if __name__ == "__main__":

    DELTA = time.time()
    print("bestgamesintheplanet [Bot]\n")

    # Frozen / not frozen, cxfreeze compatibility
    DIR = os.path.normpath(
        os.path.dirname(
            sys.executable if getattr(sys, 'frozen', False) else __file__))
    os.chdir(DIR)  # The current dir is the script home

    # Files
    TOKENS_FILE = "tokens.json"
    TUMBLR_DONE_FILE = "tumblr_done.json"
    TWITTER_DONE_FILE = "twitter_done.json"
    QBOT_FILE = "qbot.json"

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
        with open(TUMBLR_DONE_FILE, 'r') as f:
            DONE = json.load(f)
    except (IOError, ValueError):
        DONE = {}

    # Queue new games
    GAMES = get_games("https://itch.io/games")
    GAMES = {k: v for k, v in GAMES.items() if k not in DONE}

    # The game url is the 'k'ey
    print("Looking for new games...")
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

        # Image download

        image = v['gif'] if v['gif'] else v['image']

        name, ext = os.path.splitext(os.path.basename(image))
        imagename = "".join(c
                            for c in f"{v['author']}_{v['title']}_{name}{ext}"
                            if c.isalnum() or c in ["-", "_", "."]).strip()

        imagefile = os.path.normpath(os.path.join(DIR, "images", imagename))

        if not os.path.isfile(imagefile):
            with urlopen(image) as r, open(imagefile, 'wb') as f:
                shutil.copyfileobj(r, f)
                time.sleep(5)  # Decent rest

        # Queue

        try:
            result = API.create_photo(
                "bestgamesintheplanet",
                state="queue",
                tags=tags,
                format="markdown",
                caption=f"{title}{description}{price}",
                data=imagefile
                # source=f"{v['gif'] if v['gif'] else v['image']}"
            )
        except ConnectionError:
            result = False
            print(f"ConnectionError {imagefile}")

        if result:
            print(f"\nNew {k} ")
            print(f"Downloaded {image}")
            DONE[k] = v
            with open(TUMBLR_DONE_FILE, "w") as f:
                json.dump(DONE, f)

    # Info log
    COUNT = len(GAMES)
    print(
        f"\n{COUNT} game{'s' if COUNT != 1 else ''} found ({round(time.time()-DELTA)}s)\n"
    )

    # Queue on Qbot
    qbotqueuer.queue_games(TUMBLR_DONE_FILE, TWITTER_DONE_FILE, QBOT_FILE)
