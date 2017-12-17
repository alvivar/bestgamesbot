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


def queue_games(tumblrjf,
                twitterjf,
                qbotjf,
                *,
                imagepath="images",
                qbot_queue_size=10):
    """ Queue the tumblr scrapped data into QBot, keeping a registry. 'jf'
    parameters are mean to be json dictionary files. """

    print("Queing Tumblr into QBot...")

    # Frozen / not frozen, cxfreeze compatibility

    cdir = os.path.normpath(
        os.path.dirname(
            sys.executable if getattr(sys, 'frozen', False) else __file__))
    os.chdir(cdir)  # The current dir is the script home

    # Files

    if not os.path.exists(imagepath):
        os.makedirs(imagepath)

    # Get new tweets from the tumblr queue

    tumblrq = json.load(open(tumblrjf, "r"))

    try:
        twitterq = json.load(open(twitterjf, "r"))
    except (IOError, ValueError):
        twitterq = {}

    newq = {k: v for k, v in tumblrq.items() if k not in twitterq}
    newq = update_games(newq, limit=14)  # Fresh

    # Save queued

    twitterq = {**twitterq, **newq}  # Old + new twitter queued

    with open(twitterjf, "w") as f:
        json.dump(twitterq, f)

    # Queue the new tweets on QBot

    qbot = json.load(open(qbotjf, "r"))

    for key, val in newq.items():

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

        # Twitter account search TODO

        # The message
        text = f"{val['title']} ({val['author']})\n{price_title} {platforms_title} {key}"
        image = f"{val['gif'] if val['gif'] else val['image']}"

        # Download image
        name, ext = os.path.splitext(os.path.basename(image))
        imagename = "".join(
            c for c in f"{val['author']}_{val['title']}_{name}{ext}"
            if c.isalnum() or c in ["_", "."]).strip()

        imagefile = os.path.normpath(os.path.join(cdir, imagepath, imagename))

        with urllib.request.urlopen(image) as rp, open(imagefile, 'wb') as of:
            print(f"Downloading: {val['title']} {image}")
            shutil.copyfileobj(rp, of)

        # Queue
        qbot['messages'].append({"text": text, "image": imagefile})

    # Update
    with open(qbotjf, "w") as f:
        json.dump(qbot, f)


if __name__ == "__main__":

    TUMBLRJSON = "tumblr_done.json"
    TWITTERJSON = "twitter_done.json"
    QBOTJSON = r"C:\adros\code\python\bestgamesintheplanet\build\exe.win-amd64-3.6\qbot.json"

    queue_games(TUMBLRJSON, TWITTERJSON, QBOTJSON)
