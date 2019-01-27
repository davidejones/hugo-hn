#!/usr/bin/env python3
import asyncio
import logging
import re
import requests
#import sh
import sys
import time
import yaml
from datetime import datetime
from os import makedirs
from pathlib import Path
from aiohttp import ClientSession

TEMPLATE = """\
---
{front_matter}
---

{content}
"""

ROOT_DIR = Path.cwd()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def timing(f):
    """
    decorator to time a function and print it
    :param f: function to wrap
    :return: wrapped function
    """
    def wrap():
        start = time.time()
        f()
        end = time.time()
        logger.info(f"{f.__name__} took {end - start!r}")
    return wrap


def slugify(name):
    """
    Takes a article name and returns a slug appropriate version using hyphens
    :param name: string to be converted
    :return: converted string
    """
    out = re.sub(r'[^\w\d\s]', '', name)
    return re.sub(r'\s', '-', out)


def create_item(item):
    """
    Takes a hacker news json object and creates a hugo markdown page from it
    :param item: dict of article data
    """
    yml = {}
    slug = slugify(item.get('title'))
    makedirs('./content/post/', exist_ok=True)
    file_name = './content/post/{}.md'.format(slug)
    with open(file=file_name, mode='w', encoding='utf-8') as f:
        yml['date'] = datetime.fromtimestamp(item.get('time')).isoformat()
        yml['linkurl'] = item.get('url')
        yml['slug'] = slug
        yml['tags'] = []
        yml['categories'] = ["{}".format(item.get('type'))] if item.get('type', None) else []
        f.write(TEMPLATE.format(front_matter=yaml.dump(yml).strip(), content=""))


def hugo_build():
    """
    Builds the hugo site
    We overwrite the baseurl all other settings are fine
    """
    hugo = sh.hugo.bake(_cwd=str(ROOT_DIR))
    hugo('--baseURL=https://davidejones.github.io/hugo-hn/', [], _out=sys.stdout)


def get_content_sync(data):
    """
    Synchronously hit each hacker news article item for download.
    :param data: tuple of url and article type
    :return: list of json responses
    """
    responses = []
    for url, article_type in data:
        response = requests.get(url)
        for article_id in response.json():
            item_request = requests.get('https://hacker-news.firebaseio.com/v0/item/{}.json'.format(article_id))
            item = item_request.json()
            item['type'] = article_type
            responses.append(item)
    return responses


async def get_content_async(data):
    """
    Asynchronously hit each hacker news article item for download.
    :param data: tuple of url and article type
    :return: list of json responses
    """
    parent_tasks = []
    child_tasks = []
    async with ClientSession(loop=asyncio.get_event_loop()) as session:
        for url, article_type in data:
            parent_tasks.append(asyncio.create_task(fetch(url, session)))
        results = await asyncio.gather(*parent_tasks)
        for index, section in enumerate(results):
            _, article_type = data[index]
            for article_id in section:
                child_tasks.append(asyncio.create_task(
                    fetch(f'https://hacker-news.firebaseio.com/v0/item/{article_id}.json', session, article_type)))
        return await asyncio.gather(*child_tasks)


async def fetch(url, session, article_type=None):
    """
    Async fetch returning
    :param url: url to hit
    :param session: open session to make calls with
    :param article_type: the type name of the article for front matter
    :return: json response
    """
    async with session.get(url) as response:
        data = await response.json()
        if article_type:
            data['type'] = article_type
        return data


@timing
def main():
    """
    Entry function that grabs hacker news content saves it and builds the html site
    """
    id_data = [('https://hacker-news.firebaseio.com/v0/topstories.json', 'story'),
               ('https://hacker-news.firebaseio.com/v0/askstories.json', 'ask'),
               ('https://hacker-news.firebaseio.com/v0/showstories.json', 'show'),
               ('https://hacker-news.firebaseio.com/v0/jobstories.json', 'job')]

    # responses = get_content_sync(id_data)
    responses = asyncio.run(get_content_async(id_data))

    for item in responses:
        create_item(item)

    hugo_build()


if __name__ == '__main__':
    main()
