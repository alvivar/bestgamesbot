""" This script queues

This script reads the current queued games and usin QBot, queues them again
for Twitter.

But first it tries to update his data from itch.io, and it downloads the
image/gif into a folder as this is needed for the tweet to work. """

import json
import os
import sys

import urllib.request
import shutil

from itchioscrapper import update_games

if __name__ == "__main__":

    # Frozen / not frozen, cxfreeze compatibility

    DIR = os.path.normpath(
        os.path.dirname(
            sys.executable if getattr(sys, 'frozen', False) else __file__))
    os.chdir(DIR)  # The current dir is the script home

    # Files

    TUMBLRJSON = "tumblr_done.json"
    TWITTERJSON = "twitter_done.json"
    QBOTJSON = r"C:\adros\code\python\bestgamesintheplanet\build\exe.win-amd64-3.6\qbot.json"

    IMAGEPATH = "images"

    if not os.path.exists(IMAGEPATH):
        os.makedirs(IMAGEPATH)

    # Get new tweets from the tumblr queue

    TUMBLR_Q = json.load(open(TUMBLRJSON, "r"))

    try:
        TWITTER_Q = json.load(open(TWITTERJSON, "r"))
    except (IOError, ValueError):
        TWITTER_Q = {}

    NEW_Q = {k: v for k, v in TUMBLR_Q.items() if k not in TWITTER_Q}
    NEW_Q = update_games(NEW_Q, limit=14)  # Fresh

    # Save queued

    TWITTER_Q = {**TWITTER_Q, **NEW_Q}  # Old + new twitter queued

    with open(TWITTERJSON, "w") as f:
        json.dump(TWITTER_Q, f)

    # Queue the new tweets on QBot

    QBOT = json.load(open(QBOTJSON, "r"))

    for key, val in NEW_Q.items():

        # Data
        win = "Windows " if val['windows'] else ""
        mac = "Mac " if val['mac'] else ""
        lin = "Linux " if val['linux'] else ""
        web = "Web " if val['web'] else ""
        android = "Android " if val['android'] else ""

        platforms = (win + mac + lin + web + android).strip()
        platforms_title = platforms.replace(" ", ", ")
        platforms_title = f"({platforms_title})" if platforms_title else ""

        price_title = f"Buy it for {val['price']}" if val[
            'price'] else "Free to play"

        text = f"{val['title']} ({val['author']})\n{price_title} {platforms_title} {key}"
        image = f"{val['gif'] if val['gif'] else val['image']}"

        # Download image
        imagename = os.path.basename(image)
        imagefile = os.path.normpath(os.path.join(DIR, IMAGEPATH, imagename))

        with urllib.request.urlopen(image) as rp, open(imagefile, 'wb') as of:
            print(f"Downloading: {val['title']} {image}")
            shutil.copyfileobj(rp, of)

        # Queue
        QBOT['messages'].append({"text": text, "image": imagefile})

    # Update
    with open(QBOTJSON, "w") as f:
        json.dump(QBOT, f)
