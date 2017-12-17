""" This script queues

This script reads the current queued games and usin QBot, queues them again
for Twitter.

But first it tries to update his data from itch.io, and it downloads the
image/gif into a folder as this is needed for the tweet to work. """

import json
import os
import sys
from itchioscrapper import update_games


def queue_tweet(title, author, price, platformslist, url, imagepath):
    """
    Title (Author)
    Price (platforms) > url
    Image
    """

    pass


if __name__ == "__main__":

    # Current dir is the script home + Frozen / not frozen, cxfreeze
    # compatibility

    DIR = os.path.normpath(
        os.path.dirname(
            sys.executable if getattr(sys, 'frozen', False) else __file__))
    os.chdir(DIR)

    # Get new tweets from the tumblr queue

    TUMBLR_Q = json.load(
        open(
            r"C:\adros\code\python\bestgamesintheplanet\build\exe.win-amd64-3.6\tumblr_done.json",
            "r"))

    try:
        TWITTER_Q = json.load(open("twitter_done.json", "r"))
    except (IOError, ValueError):
        TWITTER_Q = {}

    NEW = {k: v for k, v in TUMBLR_Q.items() if k not in TWITTER_Q}
    NEW = update_games(NEW, limit=14)  # Fresh

    # Save old queued

    TWITTER_Q = {**TWITTER_Q, **NEW}  # Old + new twitter queued

    with open("twitter_done.json", "w") as f:
        json.dump(TWITTER_Q, f)

    # Queue the new tweets on QBot

    QBOT = json.load(
        open(
            r"C:\adros\code\python\bestgamesintheplanet\build\exe.win-amd64-3.6\qbot.json",
            "r"))
