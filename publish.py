#!/usr/bin/env python3

import logging
import re
import requests
import sh
import sys
import time
import yaml
from datetime import datetime
from os import makedirs
from pathlib import Path

TEMPLATE = """\
---
{front_matter}
---

{content}
"""

ROOT_DIR = Path.cwd()
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


@timing
def main():
    """
    Entry function that grabs hacker news content saves it and builds the html site
    """
    end_points = {'topstories': 'story', 'askstories': 'ask', 'showstories': 'show', 'jobstories': 'job'}
    for point, type in end_points.items():
        items_request = requests.get('https://hacker-news.firebaseio.com/v0/{}.json'.format(point))
        for id in items_request.json():
            item_request = requests.get('https://hacker-news.firebaseio.com/v0/item/{}.json'.format(id))
            item = item_request.json()
            item['type'] = type
            create_item(item)
    hugo_build()


if __name__ == '__main__':
    main()
