""" Itch.io scrapper that downloads popular games data. """

import json
import os
import sys
import time
import urllib.parse

import requests
from bs4 import BeautifulSoup


def chunker(seq, size):
    """ Zip a list into chunks. """
    return [seq[pos:pos + size] for pos in range(0, len(seq), size)]


def get_games(url):
    """ Returns a dictionary with all the games data from the games directory
    or search result page on itch.io. """

    headers = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    games = {}
    for data in soup.find_all("div", "game_cell"):

        url = data.find("a", "thumb_link")['href']
        title = data.find("div", "game_title").a.text
        description = data.find("div", "game_text")
        author = data.find("div", "game_author").a.text
        author_url = data.find("div", "game_author").a['href']
        price = data.find("div", "price_value")

        image = data.find("div", "game_thumb")
        if image.has_attr("data-background_image"):
            # Normal itch.io browse
            image = image['data-background_image']
        else:
            # On search result pages
            image = image['style'].split("('")[1].split("')")[0] if image[
                'style'] else False

        gif = data.find("div", "gif_overlay")

        windows = data.find("span", "icon-windows8")
        mac = data.find("span", "icon-apple")
        linux = data.find("span", "icon-tux")
        web = data.find("span", "web_flag")
        android = data.find("span", "icon-android")

        games[url] = {
            'title': title,
            'description': description.text if description else False,
            'author': author,
            'author_url': author_url,
            'price': price.text if price else False,
            'image': image,
            'gif': gif['data-gif'] if gif else False,
            'windows': True if windows else False,
            'mac': True if mac else False,
            'linux': True if linux else False,
            'web': True if web else False,
            'android': True if android else False,
            'time': time.time()
        }

    return games


def find_games(search, *, filterkeys=[], url="https://itch.io/search?q="):
    """ Search and return games, can also filter the result by key. """
    clean_search = urllib.parse.quote_plus(search)
    games = get_games(f"{url}{clean_search}")

    if filterkeys:
        filtered = {}
        for k, v in games.items():
            if k in filterkeys:
                filtered[k] = v
        games = filtered

    return games


def update_games(gamesdict):
    """ Read a dictionary that contains itch.io games urls as keys, and return
    another dictionary with the game data updated. """

    limit = 10
    updated = {}
    for key, val in gamesdict.items():
        print(f"Updating {key}")
        game = find_games(f"{val['title']} {val['author']}", filterkeys=[key])
        if game:
            updated[key] = game[key]

        limit -= 1
        if limit <= 0:
            break

    return updated


if __name__ == "__main__":

    DELTA = time.time()

    # Frozen / not frozen, cxfreeze compatibility
    DIR = os.path.normpath(
        os.path.dirname(
            sys.executable if getattr(sys, 'frozen', False) else __file__))
    os.chdir(DIR)

    # GAMES = get_games("https://itch.io/games")

    # GAMES = find_games(
    #     "Bum Bag Bangin' SeaDads",
    #     filterkeys=["https://seadads.itch.io/bum-bag-bangin"])

    OLDGAMES = json.load(
        open(
            r"C:\adros\code\python\bestgamesintheplanet\build\exe.win-amd64-3.6\done.json",
            'r'))

    GAMES = update_games(OLDGAMES)

    with open("games.json", "w") as f:
        json.dump(GAMES, f)

    print(f"Done! ({round(time.time()-DELTA)}s)")
