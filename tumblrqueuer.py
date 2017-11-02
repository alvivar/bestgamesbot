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

    # frozen / not frozen, cxfreeze compatibility
    DIR = os.path.normpath(
        os.path.dirname(
            sys.executable if getattr(sys, 'frozen', False) else __file__))
    os.chdir(DIR)

    # Files
    TOKENS_FILE = "tokens.json"
    DONE_FILE = "done.json"

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
        print(
            f"Tumblr tokens are needed! Fill out {TOKENS_FILE}\nAnd try again..."
        )
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
        DONE = []

    # Queue new games
    GAMES = itchioscrapper.get_games()
    GAMES = {k: v for k, v in GAMES.items() if k not in DONE}

    for k, v in GAMES.items():

        price = f"Buy it for {v['price']}" if v['price'] else "Free to play"

        win = "Windows " if v['windows'] else ""
        mac = "Mac " if v['mac'] else ""
        lin = "Linux " if v['linux'] else ""
        web = "Web " if v['web'] else ""
        android = "Android " if v['android'] else ""

        platforms = (win + mac + lin + web + android).strip()
        platforms_title = platforms.replace(" ", ", ")

        tags = f"{v['author']} {v['title']} {platforms}"
        tags = re.split("[^0-9a-zA-Z]", tags)
        tags = [t.lower() for t in tags if t]

        title = f"[{v['title']}]({k}) ([{v['author']}]({v['author_url']}))"

        API.create_photo(
            "bestgamesintheplanet",
            state="queue",
            tags=["indie", "games", "itchio"] + tags,
            format="markdown",
            caption=
            f"# {title}\n\n## {v['description']}\n\n### [{price}]({k}) ({platforms_title})",
            source=f"{v['gif'] if v['gif'] else v['image']}")

        print(f"New game found: {k}")

        DONE.append(k)
        with open(DONE_FILE, "w") as f:
            json.dump(DONE, f)

    print(f"\nAll done! ({round(time.time()-DELTA)}s)")
    input("OK?")
