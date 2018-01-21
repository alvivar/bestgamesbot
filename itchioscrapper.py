"""
    Itch.io data scrapper, including games directory, search and twitter
    username from the profile.
"""

import json
import os
import sys
import time
from urllib.parse import quote_plus, urlparse

import requests
from bs4 import BeautifulSoup


def chunker(seq, size):
    """
        Zip a list into chunks.
    """
    return [seq[pos:pos + size] for pos in range(0, len(seq), size)]


def get_games(url, includetwitter=False, rest=5):
    """
        Returns a dictionary with all the games data from the games directory
        or search result page on itch.io.
    """

    headers = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }
    page = requests.get(url, headers=headers)
    time.sleep(rest)

    games = {}
    soup = BeautifulSoup(page.content, "html.parser")
    for data in soup.find_all('div', 'game_cell'):

        url = data.find('a', 'thumb_link')['href']
        title = data.find('div', 'game_title').a.text
        description = data.find('div', 'game_text')
        author = data.find('div', 'game_author').a.text
        author_url = data.find('div', 'game_author').a['href']
        twitter = get_twitter(author_url) if includetwitter else False
        price = data.find('div', 'price_value')

        image = data.find('div', 'game_thumb')
        if image.has_attr('data-background_image'):
            # Normal itch.io browse
            image = image['data-background_image']
        else:
            # On search result pages
            image = image['style'].split("('")[1].split("')")[0] if image[
                'style'] else False

        gif = data.find('div', 'gif_overlay')

        windows = data.find('span', 'icon-windows8')
        mac = data.find('span', 'icon-apple')
        linux = data.find('span', 'icon-tux')
        web = data.find('span', 'web_flag')
        android = data.find('span', 'icon-android')

        games[url] = {
            'title': title,
            'description': description.text if description else False,
            'author': author,
            'author_url': author_url,
            'twitter': twitter if twitter else False,
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


def find_games(search,
               *,
               filterkeys=[],
               includetwitter=False,
               url="https://itch.io/search?q="):
    """
        Search and return games, can also filter the result by key.
    """
    clean_search = quote_plus(search)
    games = get_games(f"{url}{clean_search}", includetwitter=includetwitter)

    if filterkeys:
        filtered = {}
        for k, v in games.items():
            if k in filterkeys:
                filtered[k] = v
        games = filtered

    return games


def update_games(gamesdict, *, limit=10, includetwitter=False):
    """
        Read a dictionary that contains itch.io games urls as keys, and return
        another dictionary with the game data updated.
    """

    updated = {}
    for key, val in gamesdict.items():

        if limit <= 0:
            break

        game = find_games(
            f"{val['title']}", filterkeys=[key], includetwitter=includetwitter)
        if game:
            print(f"Updating {key}")
            updated[key] = game[key]
            limit -= 1
        else:
            print(f"Not found {key}")

    return updated


def get_twitter(url, rest=5):
    """
        Return the first Twitter user name from any page.
    """

    headers = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }
    page = requests.get(url, headers=headers)
    time.sleep(rest)

    soup = BeautifulSoup(page.content, "html.parser")
    for a in soup.find_all("a", href=True):
        if "twitter.com/" in a['href']:
            url = urlparse(a['href'])
            handler = url.path.replace('/', ' ').strip().split()[0]
            return "@" + handler.lower()

    return False


def update_games_twitter(gamesdict):
    """
        Updates the 'twitter' key for all games in dictionary, assumming main
        keys as urls to a page that contains the Twitter link.
    """
    update = {}
    for k, v in gamesdict.items():
        twitter = get_twitter(k)
        update[k] = v
        update[k]['twitter'] = twitter

        if twitter:
            print(f"Found {twitter} in {k}")

    return update


if __name__ == "__main__":

    DELTA = time.time()

    # Frozen / not frozen, cxfreeze compatibility
    DIR = os.path.normpath(
        os.path.dirname(
            sys.executable if getattr(sys, 'frozen', False) else __file__))
    os.chdir(DIR)

    # Test stuff

    GAMES = get_games("https://itch.io/games")

    # GAMES = find_games(
    #     "Bum Bag Bangin'",
    #     filterkeys=["https://seadads.itch.io/bum-bag-bangin"])

    # OLDGAMES = json.load(
    #     open(
    #         r"C:\adros\code\python\bestgamesintheplanet\build\exe.win-amd64-3.6\tumblr_done.json",
    #         'r'))

    # GAMES = update_games(OLDGAMES)

    with open("games.json", "w") as f:
        json.dump(GAMES, f)

    print(get_twitter("https://matnesis.itch.io/"))

    print(f"\nDone! ({round(time.time()-DELTA)}s)")
