# #!/usr/bin/env python3

from datetime import datetime
import re
from pathlib import Path
import time
import yaml
import asyncio
import logging
import aiohttp
import aiofile
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TEMPLATE = """\
---
{front_matter}
---

{content}
"""


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


async def write_file(data):
    file_name, data_out = '', ''
    data_id = data.get('id')
    data_type = data.get('type')
    if data_type in ('story', 'job'):
        slug = slugify(data.get('title'))
        data['date'] = datetime.fromtimestamp(data.get('time')).isoformat()
        data['linkurl'] = data.get('url')
        data['slug'] = slug
        data['tags'] = []
        data['categories'] = []
        if data.get('time', None):
            del data['time']
        if data.get('url', None):
            del data['url']
        if data.get('type', None):
            data['categories'] = ["{}".format(data.get('type'))]
            del data['type']
        file_name = f'./content/en/post/{slug}.md'
        data_out = TEMPLATE.format(front_matter=yaml.dump(data).strip(), content="")
    elif data_type == 'comment':
        file_name = f'./data/post/{data_id}.yaml'
        data_out = yaml.dump(data)
    # lets write the file
    if file_name:
        async with aiofile.async_open(file_name, 'w+') as f:
            await f.write(data_out)


async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def worker(name, queue):
    while True:
        # Get a "work item" out of the queue.
        url = await queue.get()

        # download the json
        json_data = await fetch(url)

        # This data may add more to the queue lets check
        if type(json_data) is list:
            # list of ids e.g [123, 456]
            for article_id in json_data[:1]:
                queue.put_nowait(f'https://hacker-news.firebaseio.com/v0/item/{article_id}.json')
        elif type(json_data) is dict:
            # an individiual record lets add child records to the queue
            for comment_id in json_data.get('kids', []):
                queue.put_nowait(f'https://hacker-news.firebaseio.com/v0/item/{comment_id}.json')

            # lets write this record out as a file
            await write_file(json_data)

        # Notify the queue that the "work item" has been processed.
        queue.task_done()

        logger.info(f'{name} has url {url}')


async def start():
    num_workers = 3

    # Create a queue that we will use to store our "workload".
    queue = asyncio.Queue()

    # build initial urls
    urls = [f'https://hacker-news.firebaseio.com/v0/{name}.json' for name in
            ('topstories', 'askstories', 'showstories', 'jobstories')]

    # add initial urls to queue
    for url in urls:
        queue.put_nowait(url)

    # Create worker tasks to process the queue concurrently.
    tasks = []
    for i in range(num_workers):
        task = asyncio.create_task(worker(f'worker-{i}', queue))
        tasks.append(task)

    # Wait until the queue is fully processed.
    await queue.join()

    # Cancel our worker tasks.
    for task in tasks:
        task.cancel()


@timing
def main():
    logger.info("Starting publish...")

    # create dirs
    Path('./content/en/post/').mkdir(exist_ok=True)
    Path('./data/post/').mkdir(exist_ok=True)

    # Download all json and create files
    # asyncio.run(start())
    asyncio.get_event_loop().run_until_complete(start())

    logger.info("Building site...")
    subprocess.run(["hugo", "--verbose"])


if __name__ == '__main__':
    main()
