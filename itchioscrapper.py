""" Itch.io scrapper that downloads popular games data. """

import json
import os
import sys
import time

import requests
from bs4 import BeautifulSoup


def chunker(seq, size):
    """ Zip a list into chunks. """
    return [seq[pos:pos + size] for pos in range(0, len(seq), size)]


def get_games():
    """ Returns a dictionary with all the games data. """

    url = "https://itch.io/games"
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

        image = data.find("div", "game_thumb")['data-background_image']
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
            'android': True if android else False
        }

    return games


if __name__ == "__main__":

    # frozen / not frozen, cxfreeze compatibility
    DIR = os.path.normpath(
        os.path.dirname(
            sys.executable if getattr(sys, 'frozen', False) else __file__))
    os.chdir(DIR)

    DELTA = time.time()

    GAMES = get_games()

    with open("games.json", "w") as f:
        json.dump(GAMES, f)

    print(f"Done! ({round(time.time()-DELTA)}s)")
